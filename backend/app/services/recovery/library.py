"""Thin wrapper for loading recovery content from the JSON library.

The actual content lives in docs/recovery_content/recovery_library.json.
This module provides typed access for use in the recovery engine.
"""

import json
from pathlib import Path
from functools import lru_cache

LIBRARY_PATH = Path(__file__).resolve().parents[4] / "docs" / "recovery_content" / "recovery_library.json"


@lru_cache
def load_library() -> dict:
    with open(LIBRARY_PATH) as f:
        return json.load(f)


def get_category_data(category: str) -> dict | None:
    lib = load_library()
    return lib.get("categories", {}).get(category)


def get_triage_questions() -> list[dict]:
    return load_library().get("triage_questions", [])


def list_categories() -> list[str]:
    return list(load_library().get("categories", {}).keys())
