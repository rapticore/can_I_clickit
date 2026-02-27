# Web App (Next.js 15 / React 19 / Tailwind CSS v4)

Multi-page authenticated web interface for Can I Click It? with two UX modes:

- **Simple Mode** — Large text, emoji verdicts, one-step-at-a-time guidance. Designed for non-technical users.
- **Expert Mode** — Signal tables, confidence scores, analysis tiers, latency metrics, and raw JSON output.

## Pages

| Route | Description |
|-------|-------------|
| `/login` | Email + password sign-in |
| `/register` | Account creation, displays generated API key |
| `/dashboard` | Main scan interface (paste text/URL, get verdict) |
| `/history` | Paginated scan history (cards in Simple, table in Expert) |
| `/recovery` | Triage wizard + step-by-step recovery checklists |
| `/settings` | Display mode toggle, profile, API key management |

## Run with Docker

Use the root stack:

```bash
cd infra
docker compose up --build
```

Then open `http://localhost:3007`.

## Run without Docker

Requires **Node.js >= 20** (Tailwind CSS v4 needs this for native bindings).

```bash
cd frontend
npm install
npm run dev
```

If you switch Node versions, delete `node_modules` and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8880` | Backend API base URL |

## Authentication

The app uses httponly session cookies (`clickit_session`) set by the backend on login/register. No API key configuration is needed in the frontend — the cookie is sent automatically with `credentials: "include"`.

## Tech Stack

- **Next.js 15** with App Router and route groups
- **React 19** with `"use client"` components
- **Tailwind CSS v4** via `@tailwindcss/postcss` (no `tailwind.config.js`)
- Custom theme colors defined in `app/globals.css` via `@theme` block
