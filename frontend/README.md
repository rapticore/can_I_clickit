# Web Tester (Next.js)

Local UI for testing the scan API.

## Run with Docker

Use the root stack:

```bash
cd infra
docker compose up --build
```

Then open `http://localhost:3007`.

## Run without Docker

```bash
cd frontend
npm install
npm run dev
```

Set optional environment variables:

- `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8880`)
- `NEXT_PUBLIC_API_KEY` (default: empty)
