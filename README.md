# Can I Click It?

**AI-Powered Personal Safety Assistant -- A Seatbelt for the Internet**

> Before you click -- ask us. After you click -- we've got you.

---

## About This Project

**Can I Click It?** was built as part of the **Merritt College Oakland "Hacker Guard"** course. It is a working, end-to-end AI safety assistant that demonstrates how large language models can be combined with classical heuristics, machine learning classifiers, and threat intelligence feeds to solve a real consumer safety problem.

The project defines a new product category -- the **Personal AI Security Assistant (PASA)** -- that protects non-technical users from phishing, scams, and social engineering across every digital channel. It answers two questions:

1. **"Can I click this?"** -- Instant threat analysis before a user interacts with a suspicious message, link, QR code, or screenshot.
2. **"I already clicked it -- what do I do?"** -- Guided, step-by-step emergency recovery after a mistake.

Unlike traditional security tools that check URLs against static blocklists, this system analyzes the **communicative intent** of messages: is the sender trying to create urgency, impersonate a trusted contact, or manipulate the recipient into an unusual action? This catches social engineering attacks that have no malicious artifact at all.

---

## What's Working Today

This is a fully functional application you can run locally with Docker. The working system includes:

- **Tiered AI analysis pipeline** -- Three-stage detection (heuristics, ML classifiers, LLM reasoning) that routes 60-70% of scans through the fast path without an LLM call
- **FastAPI backend** with 7 REST endpoints for scanning, recovery, feedback, and health
- **10 complete recovery checklists** covering credential theft, financial fraud, identity theft, malware, gift card scams, remote access compromise, sextortion/blackmail, ransomware, pig butchering/romance scams, and general unknown threats
- **Next.js web app** with email/password registration, JWT auth, two UX modes (Simple/Expert), multi-page Tailwind CSS interface with dashboard, scan history, recovery wizard, and settings
- **Chrome extension** (Manifest V3) with link hover analysis, page trust scores, and warning interstitials
- **iOS app** (Swift/SwiftUI) with share sheet, QR scanner, voice input, Grandma Mode, and recovery flows
- **Android app** (Kotlin/Compose) with Material Design 3, ML Kit barcode scanning, and speech services
- **Full test suite** with unit, integration, and load tests
- **Docker Compose stack** that brings up the entire system in one command

---

## Architecture

```
can_I_clickit/
  backend/          Python/FastAPI -- Tiered AI analysis pipeline, JWT auth, verdict engine, recovery engine
  frontend/         Next.js 15/React 19 -- Multi-page Tailwind CSS app with auth, two UX modes, dashboard
  mobile/ios/       Swift/SwiftUI -- iOS app with share sheet, QR scanner, voice, Grandma Mode
  mobile/android/   Kotlin/Compose -- Android app with Material Design 3
  extension/chrome/ TypeScript -- Chrome Manifest V3 extension with hover analysis
  infra/            Terraform (AWS) + Docker Compose (local dev)
  docs/             PRD, recovery content library
```

### Detection Pipeline

```
Scan Request
  --> Input Normalization (detect type, extract URLs)
  --> Cache Check (SHA-256 hash, Redis, 30-day TTL)
  --> Fast Path  [< 500ms]  Heuristics, blocklists, regex patterns, domain age
  --> ML Path    [1-2s]     Phishing classifier, intent detection, manipulation scoring
  --> LLM Path   [2-3s]     Anthropic Claude chain-of-thought analysis
  --> Verdict Engine         Aggregate signals, calibrate confidence, apply safety bias
  --> Response               Verdict + Confidence + Consequence Warning + Safe Action
```

The **safety bias** ensures that when the system is uncertain, it defaults to "suspicious" rather than "safe." Low-confidence verdicts never produce a safe result.

---

## How to Run

### Prerequisites

- **Docker** and **Docker Compose** (v2+)
- **Git**
- **Node.js >= 20** (for local frontend development without Docker)
- Ports 8880, 3007, 5432, 6379, 9200, 9000, 9001 available

### 1. Clone and Start (Docker -- Recommended)

This brings up the full stack: API, PostgreSQL, Redis, Elasticsearch, MinIO, and the web tester UI.

```bash
git clone <repo-url> can_I_clickit
cd can_I_clickit/infra
docker compose up --build
```

Wait for all services to report healthy (typically 30-60 seconds), then open:

| Service | URL | Description |
|---------|-----|-------------|
| Web App | http://localhost:3007 | Register, log in, and analyze messages/URLs |
| API | http://localhost:8880 | FastAPI backend (Swagger docs at `/docs`) |
| MinIO Console | http://localhost:9001 | S3-compatible object storage UI |

Open http://localhost:3007, register an account, and you'll land on the dashboard where you can analyze suspicious messages and URLs. Toggle between **Simple Mode** (large text, emoji verdicts, step-by-step guidance) and **Expert Mode** (signal tables, confidence scores, raw JSON) in Settings.

You can also use the API directly with your per-user API key or a global key from `CLICKIT_API_KEYS`:

```bash
curl -s -X POST http://localhost:8880/v1/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-12345" \
  -d '{
    "scan_type": "text",
    "content": "URGENT: Your bank account has been suspended. Verify immediately at https://secure-account-review-now.xyz"
  }' | python3 -m json.tool
```

The response includes `threat_level`, `confidence`, `verdict_summary`, `consequence_warning`, `safe_action_suggestion`, and the full signal breakdown.

### 3. Run Tests

Run the backend test suite inside Docker against real PostgreSQL:

```bash
cd infra
docker compose --profile test run --rm api-tests
```

Or run locally with a Python virtual environment:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
```

### 4. Stop Everything

```bash
cd infra
docker compose down          # stop containers, keep data
docker compose down -v       # stop containers and delete volumes
```

---

## Running Without Docker

If you prefer running the backend natively (PostgreSQL and Redis must be available separately):

```bash
# Copy and edit environment config
cp .env.example .env
# At minimum, set CLICKIT_DATABASE_URL, CLICKIT_REDIS_URL.
# Set CLICKIT_DEBUG=true for local development (auto-generates a dev JWT secret).

# Set up Python
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start the API (port matches docker-compose)
uvicorn app.main:app --reload --port 8880

# In another terminal, start the frontend (requires Node >= 20)
cd frontend
npm install
npm run dev
```

**Note:** SQLite is not supported. The application requires PostgreSQL (`postgresql+asyncpg`) for both local and production environments. The frontend uses Tailwind CSS v4 which requires **Node.js >= 20**. If you switch Node versions, delete `node_modules` and run `npm install` again.

---

## API Endpoints

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/v1/auth/register` | None | Create account, returns JWT cookie + API key |
| POST | `/v1/auth/login` | None | Log in, returns JWT cookie |
| POST | `/v1/auth/logout` | JWT | Clear session cookie |
| GET | `/v1/auth/me` | JWT or API key | Current user profile |
| PATCH | `/v1/auth/profile` | JWT or API key | Update grandma_mode / language |
| POST | `/v1/auth/rotate-api-key` | JWT | Regenerate per-user API key |

### Scan & Analysis

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/v1/scan` | JWT or API key | Analyze text, URL, or QR data |
| POST | `/v1/scan/screenshot` | JWT or API key | Analyze screenshot via OCR (multipart upload) |
| POST | `/v1/scan/screenshot/base64` | JWT or API key | Analyze base64 screenshot payload (mobile) |
| GET | `/v1/scan/history` | JWT or API key | Paginated scan history for the current user |
| GET | `/v1/page-trust` | JWT or API key | Domain trust score for browser extension |

### Recovery & Feedback

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/v1/recovery/triage` | JWT or API key | Submit triage answers, get recovery checklist |
| GET | `/v1/recovery/checklist/{category}` | JWT or API key | Get recovery steps for a threat category |
| GET | `/v1/recovery/triage/questions` | JWT or API key | Get triage questionnaire |
| POST | `/v1/feedback` | JWT or API key | Submit verdict feedback |
| GET | `/v1/health` | None | Service health check |

All endpoints accept authentication via either a `clickit_session` JWT cookie or an `X-API-Key` header. In debug mode, unauthenticated access is allowed.

Full interactive API documentation is available at http://localhost:8880/docs when the API is running.

---

## Recovery Categories

The emergency recovery system provides guided, step-by-step checklists for 10 incident types:

| Category | Trigger | Urgency |
|----------|---------|---------|
| Credential Theft | Entered password on a suspicious site | High |
| Financial Fraud | Shared bank or credit card details | Critical |
| Identity Theft | Shared SSN, date of birth, or government ID | Critical |
| Malware / Download | Downloaded a suspicious file or app | High |
| Gift Card / Wire | Sent money via gift card, wire, or crypto | Critical |
| Remote Access | Gave someone remote access to a device | Critical |
| Blackmail / Sextortion | Received threatening email demanding payment | Medium |
| Ransomware Extortion | Email claiming files are encrypted | High |
| Pig Butchering | Online contact encouraging investment | Critical |
| General / Unknown | Not sure what happened | Medium |

Each checklist includes a calming opening ("Don't worry -- let's fix this together"), one-step-at-a-time progressive disclosure, expandable help details, quick-dial emergency contacts, and a legal disclaimer.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy (async), Alembic |
| Authentication | JWT (python-jose), bcrypt (passlib), httponly cookies, per-user API keys |
| AI / ML | Anthropic Claude (Haiku / Sonnet), custom heuristic + ML classifiers, Tesseract OCR |
| Web App | Next.js 15, React 19, Tailwind CSS v4 |
| iOS App | Swift, SwiftUI, AVFoundation, SFSpeechRecognizer |
| Android App | Kotlin, Jetpack Compose, Material Design 3, ML Kit, CameraX |
| Browser Extension | TypeScript, Chrome Manifest V3 |
| Databases | PostgreSQL 16, Redis 7, Elasticsearch 8 |
| Object Storage | MinIO (S3-compatible, local) / AWS S3 (production) |
| Infrastructure | Docker Compose (local), Terraform + AWS (ECS, RDS, ElastiCache, API Gateway) |
| CI/CD | GitHub Actions (lint, test, build, deploy) |
| Testing | pytest, pytest-asyncio, pytest-cov, Locust (load testing) |

---

## Environment Variables

All backend configuration is via environment variables prefixed with `CLICKIT_`. See [`.env.example`](.env.example) for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `CLICKIT_DATABASE_URL` | *(required)* | PostgreSQL connection string (`postgresql+asyncpg://...`) |
| `CLICKIT_REDIS_URL` | *(required)* | Redis connection string |
| `CLICKIT_JWT_SECRET_KEY` | *(required in prod)* | Secret for signing JWT tokens. Auto-set in debug mode |
| `CLICKIT_JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `CLICKIT_JWT_EXPIRY_MINUTES` | `1440` | JWT token lifetime (default 24h) |
| `CLICKIT_API_KEYS` | `[]` | JSON array of global API keys (legacy/shared access) |
| `CLICKIT_ANTHROPIC_API_KEY` | `""` | Anthropic API key for LLM reasoning tier |
| `CLICKIT_VIRUSTOTAL_API_KEY` | `""` | VirusTotal API key for domain reputation |
| `CLICKIT_FREE_TIER_DAILY_SCANS` | `5` | Daily scan limit for free-tier users |
| `CLICKIT_ENABLE_LIVE_LINK_CHECKS` | `false` | Enable live URL fetching (redirects, SSL) |
| `CLICKIT_CORS_ORIGINS` | `[]` | Allowed CORS origins (wildcard rejected in production) |
| `CLICKIT_LOG_LEVEL` | `INFO` | Logging level |

---

## Production Roadmap

This section outlines the path from the current working prototype to a production-grade service, organized in four phases.

### Phase 1: Production Hardening (Months 1-2)

**Infrastructure and reliability**

- Deploy to AWS ECS/Fargate behind API Gateway with auto-scaling (target: 10,000 concurrent users)
- Separate PostgreSQL into AWS RDS with read replicas, automated backups, and encryption at rest
- Move Redis to ElastiCache with cluster mode for high availability
- Add Elasticsearch cluster with multi-node deployment for the scam corpus
- Implement database migrations pipeline (Alembic) in CI/CD with zero-downtime rollouts
- Add structured observability: Grafana dashboards for latency p50/p95/p99, error rates, and scan tier distribution; PagerDuty alerting for SLA breaches

**Security**

- ~~Replace static API keys with JWT-based authentication (user registration + login)~~ *Done (Sprint 1)*
- Add OAuth2 flows for mobile apps
- Implement per-user rate limiting with token bucket algorithm
- Complete OWASP Top 10 audit on all endpoints
- Add ephemeral processing verification: automated tests confirming no user content persists beyond in-memory analysis
- Obtain E&O insurance before public launch

**Quality**

- Curate a test corpus of 500+ known scam messages and validate false negative rate < 1%
- Run quarterly red-team exercises with external security researchers
- Senior usability testing (5-8 participants aged 65+) and iterate on Grandma Mode

### Phase 2: Reinforcement Learning from Human Feedback -- RLHF (Months 2-4)

This is the highest-leverage improvement. The current system uses static heuristics and a general-purpose LLM. RLHF creates a compounding data advantage that gets better with every scan.

**Feedback collection pipeline**

- Instrument every verdict with a "Was this correct?" prompt (already built: thumbs up/down + false positive/false negative reporting via `/v1/feedback`)
- Store feedback in a labeled dataset: `(input, system_verdict, user_correction, confidence_delta)`
- Build a review queue for false negatives (highest priority) and false positives
- Add "Report this as a scam" for messages the system marked safe -- these are the most valuable training signals

**Reward model training**

- Train a reward model on the labeled feedback data that scores verdict quality
- Features: signal agreement count, confidence gap between system and user, threat category, input complexity
- Use the reward model to re-rank ambiguous verdicts (score 40-70) in the ML path before they escalate to the LLM tier

**Fine-tuning the classifier**

- Fine-tune a lightweight model (DistilBERT or similar) on the growing labeled corpus for phishing intent classification
- Replace the keyword-weighted classifier in `ml_path.py` with the fine-tuned model
- Target: reduce LLM tier escalation from 30-40% to under 15%, cutting per-scan cost by 60-80%
- Retrain monthly as the corpus grows; A/B test new models against the previous version

**Reinforcement learning loop**

- Implement a continuous learning pipeline: feedback -> label -> retrain -> deploy -> monitor
- Use MLflow for model versioning and experiment tracking
- Canary deployments: route 5% of traffic to the new model, compare verdict agreement and user feedback rates before full rollout
- Automated rollback if false negative rate exceeds 1% on the canary

**Active learning**

- Identify scans where the system is least confident (score 45-55) and prioritize these for human review
- Route low-confidence verdicts to a human review queue (internal team or crowdsourced via Amazon Mechanical Turk)
- Each reviewed verdict becomes a high-value training example, accelerating model improvement where it matters most

### Phase 3: Feature Expansion (Months 4-8)

**Consumer features**

- Family Guardian Dashboard: link family accounts, receive alerts when a family member encounters a high-risk threat, remotely trigger recovery guidance
- Real-time background monitoring (premium): notification-based scanning for incoming messages
- Contact impersonation detection: match incoming messages against the user's address book to detect spoofed senders
- On-device lightweight model: run common pattern detection (80% of safe verdicts) entirely on-device for zero-latency, zero-cost scans
- Multilingual expansion: add Mandarin, Hindi, Portuguese detection models

**Platform expansion**

- Publish iOS app to App Store and Android app to Google Play
- Submit Chrome extension to Chrome Web Store; adapt for Safari, Edge, Firefox
- Build web-only mode (no install) for maximum reach

**Intelligence**

- Campaign clustering: group related scam messages into campaigns (e.g., "fake USPS delivery wave targeting Northeast US") and detect new variants from known actors before they appear in public threat feeds
- Scam Trends Report: monthly publication using anonymized data for earned media and SEO

### Phase 4: Scale and Monetization (Months 8-12)

**Freemium model**

| Feature | Free | Premium ($6.99/mo) |
|---------|------|---------------------|
| Daily scans | 5 | Unlimited |
| Detection quality | Fast + ML path | Full LLM reasoning |
| Emergency recovery | Basic checklist | Personalized + quick-dial + family alert |
| Voice / Grandma Mode | Included | Included |
| Browser extension | Basic link checking | Full hover + login detection |
| Family protection | Not included | Up to 5 accounts |
| Background monitoring | Not included | Real-time |

**Partnership revenue**

- Mobile carriers: white-label integration ($0.50-$2.00/subscriber/month)
- Banks: embedded scam detection for customers with enterprise SLA
- Insurance companies: cyber insurance risk-reduction bundling
- Senior services: AARP, elder care platforms, group licensing

**Advanced AI**

- Call screening AI for scam and robocall detection (v3.0)
- Deepfake voice detection during calls
- Dark web monitoring for breach alerts
- Attachment sandbox analysis
- Transaction verification before payment execution

**Data moat**

- The reinforcement learning pipeline creates a compounding advantage: more users -> more scans -> more feedback -> better models -> fewer false negatives -> more trust -> more users
- This data flywheel is the primary competitive moat against big-tech entry (Google, Apple) and existing security vendors (Norton, Bitdefender)

---

## Project Structure

```
backend/
  app/
    api/v1/routes/         API endpoint handlers (auth, scan, recovery, feedback, health)
    core/                  Config, JWT/API-key auth, rate limiting
    services/
      auth.py              Password hashing, JWT tokens, API key generation
      analysis/            Tiered pipeline: fast_path, ml_path, llm_path
      detection/           Intent detector, link analyzer, content analyzer, OCR, QR
      verdict/             Verdict engine, confidence calibration, consequence + safe action
      recovery/            Recovery engine, triage logic, content library
    models/                Pydantic request/response schemas (auth, scan, recovery, feedback)
    integrations/          VirusTotal, PhishTank, URLhaus, Anthropic, WHOIS clients
    db/                    SQLAlchemy models, Alembic migrations
    cache/                 Redis client with hash-based verdict caching
  tests/
    unit/                  Unit tests for all services (incl. auth)
    integration/           End-to-end pipeline tests
    load/                  Locust load test config

frontend/                  Next.js 15 / React 19 / Tailwind CSS v4
  app/
    (auth)/                Login and registration pages (no navbar)
    (app)/                 Authenticated pages with navbar + footer
      dashboard/           Main scan interface (Simple & Expert modes)
      history/             Scan history with pagination
      recovery/            Triage wizard + recovery checklists
      settings/            Profile, display mode toggle, API key management
  components/
    ui/                    Button, Card, Input, Badge, Spinner, Modal
    layout/                Navbar (responsive), Footer
    scan/                  ScanForm, ScanResult, GrandmaResult, AnalystResult
    history/               HistoryCards (simple), HistoryTable (expert)
    recovery/              TriageWizard, RecoveryChecklist
    settings/              ProfileForm, GrandmaModeToggle, ApiKeyPanel
  lib/                     API client, AuthProvider, UXModeProvider

mobile/
  ios/CanIClickIt/         SwiftUI app (14 source files)
  android/app/             Kotlin/Compose app

extension/chrome/          Manifest V3 extension (14 source files)

infra/
  docker-compose.yml       Full local stack
  terraform/               AWS infrastructure as code

docs/
  recovery_content/        Recovery checklist library (JSON, 10 categories)
```

---

## Contributing

This project was built as a learning exercise at Merritt College Oakland. Contributions, feedback, and forks are welcome. If you find a bug or want to improve the detection pipeline, open an issue or submit a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Built at Merritt College Oakland -- How to Build With LLMs (2026)*
