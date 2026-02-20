import os
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.cache import redis_client
from app.core.rate_limiter import check_rate_limit
from app.db.database import Base, get_db
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True, scope="function")
def clear_globals():
    """Ensure global memoized instances don't leak closed event loops across tests."""
    import app.cache.redis_client as redis_client
    redis_client._redis_pool = None
    import app.db.database as db
    db._engine = None
    db._session_factory = None
    _MOCK_REDIS_STORE.clear()
    yield


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return os.getenv("CLICKIT_TEST_DATABASE_URL") or os.getenv(
        "CLICKIT_DATABASE_URL",
        "postgresql+asyncpg://clickit:clickit@localhost:5432/clickit",
    )


_MOCK_REDIS_STORE: dict[str, str] = {}

@pytest.fixture
def mock_redis():
    """Mock Redis for tests that don't need a live instance."""
    _MOCK_REDIS_STORE.clear()
    mock = AsyncMock()

    async def _get(key: str):
        return _MOCK_REDIS_STORE.get(key)
        
    async def _execute_command(*args, **kwargs):
        pass
    mock.execute_command = AsyncMock(side_effect=_execute_command)

    mock.get = AsyncMock(side_effect=_get)
    mock.setex = AsyncMock()
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock()
    mock.ping = AsyncMock()
    mock.pipeline = lambda: _MockPipeline(_MOCK_REDIS_STORE)
    return mock


class _MockPipeline:
    def __init__(self, store: dict[str, str]):
        self._commands: list[tuple[str, str, int | None]] = []
        self._store = store

    def incr(self, key: str):
        self._commands.append(("incr", key, None))
        return self

    def expire(self, key: str, ttl: int):
        self._commands.append(("expire", key, ttl))
        return self

    async def execute(self):
        results = []
        for command, key, _ttl in self._commands:
            if command == "incr":
                value = int(self._store.get(key) or 0) + 1
                self._store[key] = str(value)
                results.append(value)
            elif command == "expire":
                results.append(True)
        return results


@pytest.fixture(scope="session")
async def db_engine(test_database_url: str):
    """Shared PostgreSQL engine for tests (Docker/local service)."""
    from sqlalchemy.pool import NullPool
    engine = create_async_engine(
        test_database_url,
        echo=False,
        poolclass=NullPool,
    )
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:
        await engine.dispose()
        raise RuntimeError(
            "PostgreSQL test database is unavailable. Start Docker services "
            "(e.g., `cd infra && docker-compose up -d`) and verify CLICKIT_DATABASE_URL."
        ) from exc
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def _truncate_all_tables(engine) -> None:
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE'))


@pytest.fixture
async def test_db(db_engine):
    await _truncate_all_tables(db_engine)
    testing_session_local = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with testing_session_local() as session:
        yield session
    # Removed rollback here as truncate handles isolation, and rolling back closed connections drops tasks


@pytest.fixture
async def client(mock_redis, test_db):
    """Async test client with mocked Redis and PostgreSQL DB."""

    async def _override_get_db():
        yield test_db

    async def _override_rate_limit():
        return None

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[check_rate_limit] = _override_rate_limit
    
    with patch("app.cache.redis_client.get_redis", return_value=mock_redis):
        with patch("app.main.init_db_schema", return_value=None):
            with patch("app.cache.redis_client.close_redis", return_value=None):
                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as ac:
                    yield ac
                    
    app.dependency_overrides.clear()
