# Plant Intelligence Platform — IT / DevOps Installation Guide

This guide explains how to install, configure, and run the Plant Intelligence
Platform (PIP) on your own computer or server, whether it will be used only on
your **internal network** (LAN) or exposed to the **external network** (the
Internet / a remote server).

The project is open source (MIT) and hosted on GitHub:
`https://github.com/newdevelopment005/plant-intelligence-platform` (branch `master`).

---

## 1. What you are installing

The platform consists of three applications and four data services:

| Component        | Tech                    | Default port | Purpose                                   |
|------------------|-------------------------|--------------|-------------------------------------------|
| **web**          | Next.js 15 (React 19 TS) | 3000         | Web interface (browser)                   |
| **api**          | FastAPI (Python 3.12)   | 8000         | Backend REST API + admin panel            |
| **ai-service**   | FastAPI + LangGraph     | 8001         | AI assistants (chat, analysis, etc.)      |
| **postgres**     | PostgreSQL 16           | 5432         | Main relational database                  |
| **neo4j**        | Neo4j 5.x               | 7474 / 7687 | Knowledge graph                          |
| **qdrant**       | Qdrant                  | 6333 / 6334 | Vector embeddings for AI                  |
| **redis**        | Redis 7                 | 6379         | Cache, sessions, background jobs          |
| **nginx**        | Nginx (optional)        | 80 / 443     | Reverse proxy for production              |

The AI chat can run in two modes (see section 6):
- **Local mode** using [Ollama](https://ollama.com) (default, offline-friendly),
- **Cloud mode** using an external LLM API key (OpenAI-compatible).

---

## 2. Hardware and OS requirements

| Requirement      | Minimum (small team)      | Recommended               |
|------------------|---------------------------|---------------------------|
| CPU              | 4 cores                   | 8+ cores                  |
| RAM              | 8 GB                      | 16 GB+ (needed for local LLM) |
| Disk             | 20 GB free                | 50 GB+ (SSD)              |
| OS               | Linux / macOS / Windows   | Linux server (Ubuntu 22.04 LTS recommended) |

- Windows users: install **Docker Desktop** (with the built-in WSL2 or Hyper-V backend — no separate WSL install is required).
- A GPU is **not required** for the included `gemma2:2b` model, but makes larger models faster if you install them.

Software you will need on the host machine:
- **Docker** + **Docker Compose** plugin (recommended path)
- **Git** (to clone the repository)
- **Ollama** (only if running the AI in local mode)

> No Node.js or Python is required on the host when using the Docker path.

---

## 3. Network topologies

### 3.1 Internal network (department LAN)
All services run on a single computer or server inside the department network.
Users reach the platform at `http://<server-ip>:3000`. No public internet exposure.

```
[Browser] --> http://server-ip:3000 --> nginx 80 --> web / api / ai-service (same host)
```

### 3.2 External network (Internet / remote server)
The platform runs on a public server. You expose it through a reverse proxy with
HTTPS, a DNS name, and a firewall. Users reach it via `https://platform.yourorg.org`.

```
[Internet users] --> DNS --> Public IP:443 --> nginx (SSL) --> web / api / ai-service
```

### 3.3 Hybrid (frontend hosted, backend self-hosted)
The web frontend is deployed to a static host (e.g. Vercel) while the API and
data services stay on your own server. See `DEPLOYMENT.md` for that option.

---

## 4. Environment variables reference

Copy the template file and edit it:

```bash
cp .env.example .env
```

Frontend settings that are read **inside the Docker Compose environment** are
defined separately. The key variables:

### Backend / API (`api` service)

| Variable            | Default                                  | Notes                                            |
|---------------------|------------------------------------------|--------------------------------------------------|
| `ENVIRONMENT`       | `development`                            | `production` in production                       |
| `DEBUG`             | `False`                                  | Keep `False` in production                       |
| `SECRET_KEY` / `JWT_SECRET_KEY` | (generated)                | **Must be changed**; long random string          |
| `DATABASE_URL`      | `postgresql+asyncpg://...`               | PostgreSQL connection                            |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | —            | Used by the postgres container                   |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | —              | Neo4j credentials                                |
| `QDRANT_URL`        | `http://localhost:6333`                  | or `http://qdrant:6333` inside compose           |
| `REDIS_URL`         | `redis://localhost:6379/0`               | or `redis://redis:6379/0` inside compose         |
| `CORS_ORIGINS`      | (comma-separated list)                  | **In production, set to your exact frontend URL** (e.g. `https://platform.yourorg.org`). Internal network: `http://server-ip:3000`. |
| `API_HOST`, `API_PORT`, `API_WORKERS` | `0.0.0.0`, `8000`, `4` | Bind/port/worker count. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` | — | Required for email verification & password reset. Can also be set per-department in the Admin panel. |
| `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_MINI_MODEL` | — | Cloud AI mode (see section 6). |
| `USE_LOCAL_LLM`      | official default enabled       | `True` = use Ollama; `False` = use OpenAI API    |
| `OLLAMA_BASE_URL`    | `http://localhost:11434/v1`    | Where the API finds Ollama. Inside compose: `http://host.docker.internal:11434/v1` (see section 6). |
| `OLLAMA_MODEL`       | `gemma2:2b`                    | Main chat model                                  |
| `OLLAMA_MINI_MODEL`  | `gemma2:2b`                    | Lightweight tasks                                |
| `AI_SERVICE_URL`     | `http://localhost:8001`         | URL of the ai-service. Inside compose: `http://ai-service:8001`. |
| `STORAGE_*`          | local          | Where uploaded files/images are stored. |

### Web frontend (`web` service)

| Variable                    | Default                  | Notes                                        |
|-----------------------------|--------------------------|----------------------------------------------|
| `NEXT_PUBLIC_API_URL`       | `http://localhost:8000/api/v1` | **Public URL of the API** that the browser calls. Internal: `http://server-ip:8000/api/v1`. Behind nginx: `/api/v1` on the same host. |
| `NEXT_PUBLIC_AI_URL`        | `http://localhost:8001`  | Public URL of the ai-service (for direct AI calls) |
| `BACKEND_URL`               | `http://localhost:8000`  | **Server-side** URL used by the Next.js proxy for images/uploads and the AI chat proxy. |

> Important — the Docker Compose file (`docker-compose.yml`) hardcodes the web
> service's public env vars (`NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_AI_URL`) and does
> **not** set `BACKEND_URL`. These are inlined into the Next.js build, so to
> change them you edit the `web` service section of `docker-compose.yml`, then
> rebuild:
>
> ```yaml
>   web:
>     environment:
>       - NEXT_PUBLIC_API_URL=http://<server-ip-or-origin>/api/v1
>       - NEXT_PUBLIC_AI_URL=http://<server-ip-or-origin>:8001/api/v1
>       - BACKEND_URL=http://api:8000
> ```
>
> `BACKEND_URL` must be `http://api:8000` so the images/AI proxies on the `web`
> container reach the API container (never `localhost` inside a container).
> `.env` values for the **api/ai-service** containers come from `.env.example`.

> Do not commit real secrets. `.env` is in `.gitignore`.

---

## 5. Installation — Docker (recommended)

### 5.1 Clone and configure

```bash
git clone https://github.com/newdevelopment005/plant-intelligence-platform.git
cd plant-intelligence-platform
cp .env.example .env
```

Edit `.env`:
1. Change `SECRET_KEY` / `JWT_SECRET_KEY` to a long random string.
2. Set unique database/Neo4j passwords.
3. Set `CORS_ORIGINS` to the exact URL users will type in their browser.
4. Set SMTP settings (needed for email verification).
5. If you run the AI in local mode, set `OLLAMA_BASE_URL` to reach your host's Ollama (section 6), or set `USE_LOCAL_LLM=False` with an `OPENAI_API_KEY` instead.
6. Create `apps/web/.env.local` (or set the same values in Compose) with the web URL variables, adjusting `NEXT_PUBLIC_API_URL` / `BACKEND_URL` per section 3.

### 5.2 Start the stack

```bash
docker compose up -d --build
```

This builds and starts web, api, ai-service, postgres, neo4j, qdrant, redis, and
an optional nginx reverse proxy (ports 80/443). If ports 80/443 are already in
use on your machine (or you only want the apps for now), start the app and data
services instead:

```bash
docker compose up -d web api ai-service postgres neo4j qdrant redis
```

### 5.3 Run database migrations

```bash
docker compose run --rm api alembic upgrade head
```

### 5.4 Verify

```bash
docker compose ps                 # all services should be "running"/"healthy"
curl http://localhost:8000/health # API health, expect 200 OK
```

Open the platform at `http://localhost:3000` (internal network: `http://<server-ip>:3000`).

> Production example: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build`. The production file adds extra API workers, health checks, resource limits, and restart policies.

---

## 6. Setting up the AI (Ollama)

The AI assistant needs a model server. Local mode uses Ollama on the host machine.

1. Install Ollama: https://ollama.com (Windows/macOS/Linux installers).
2. Pull the chat model:
   ```bash
   ollama pull gemma2:2b
   ```
   (entirely offline once downloaded; the model is ~1.6 GB).
3. Confirm it is running: `curl http://localhost:11434` should return `Ollama is running`.
4. In `.env`, point the API/ai-service at Ollama:
   - On Linux/macOS (Ollama on the same host): `OLLAMA_BASE_URL=http://localhost:11434/v1`
   - On Windows with Docker Desktop: `OLLAMA_BASE_URL=http://host.docker.internal:11434/v1`
   - If a remote Ollama server is used, use its address.
5. Restart the api and ai-service containers.

To use a **cloud/OpenAI-compatible** model instead:
```bash
USE_LOCAL_LLM=False
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini   # or any compatible model
OPENAI_MINI_MODEL=gpt-4o-mini
```

> Note: on a server exposed to the internet, run Ollama bound to the internal
> interface only, or keep it on a separate internal host. Do not expose it publicly.

---

## 7. Network configuration

### 7.1 Internal network (LAN) only
- Edit the `web` service in `docker-compose.yml` so browsers on other machines can reach the API (`localhost` won't work for them):
  - `NEXT_PUBLIC_API_URL=http://<server-ip>:8000/api/v1`
  - `BACKEND_URL=http://api:8000` (required for images/AI to work at all)
  Then rebuild: `docker compose up -d --build`.
- Open firewall ports on the host: **3000** (web) and optionally **8000** (API).
- Users access: `http://<server-ip>:3000`.

### 7.2 External network / production server
Recommended setup: keep everything behind one **nginx** reverse proxy with TLS.
An `infrastructure/nginx/nginx.conf` is provided for a single-host setup.

1. Point your domain DNS (A record) to the server's public IP.
2. Run the stack behind nginx, or use your distro nginx:
   - `/api/` proxies to the `api` service (port 8000), `client_max_body_size 100M`.
   - `/api/v1/ai/` proxies to `ai-service` (port 8001) with long read timeout (600s).
   - `/` proxies to the `web` service (port 3000), WebSocket upgrade headers set.
3. Issue a TLS certificate:
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d platform.yourorg.org
   ```
4. From now on `CORS_ORIGINS` must be `https://platform.yourorg.org` and
   `NEXT_PUBLIC_API_URL` should be the same-origin API path if you proxy
   `/api/` on the same domain, otherwise the full API URL.
5. Firewall: allow only `443` (and `80` for ACME). **Do not** expose postgres,
   neo4j, qdrant, redis, or Ollama publicly.
6. For multiple hosts, only the proxy host needs ports open; API/data services
   talk over an internal Docker network or private VLAN.

### 7.3 Deploying the frontend WITHOUT Vercel (alternative hosts)

You are not required to use Vercel. The web frontend is a standard Next.js 15
application, so it can be hosted almost anywhere. Pick the option that fits:

#### Option A — Run everything on one of your own servers (simplest)
This is the recommended non-Vercel path: run web + api + ai-service + databases
together with Docker on your own machine or VPS. It is fully covered in sections
5–7 of this guide. No extra build pipeline needed.

```bash
git clone https://github.com/newdevelopment005/plant-intelligence-platform.git
cd plant-intelligence-platform
cp .env.example .env        # edit secrets, SMTP, CORS, AI settings
docker compose up -d --build
docker compose run --rm api alembic upgrade head
# users reach it at http://<server-ip>:3000 or https://platform.yourorg.org
```

#### Option B — Frontend on a Node/Next.js hosting platform
Platforms that run the Next.js server (Node) work out of the box, e.g.
**Railway**, **Render**, **Fly.io**, or a plain VPS running `npm start`.
The backend (api/ai-service/databases) runs separately with Docker.

Steps that are the same everywhere:
1. Point the repo build to `apps/web` (that is the frontend root).
2. Build command: `npm install && npm run build`
3. Start command: `npm start` (port 3000).
4. Set these environment variables on the hosting platform:

   | Variable | Value to set |
   |----------|--------------|
   | `NEXT_PUBLIC_API_URL` | Public URL of your backend API, e.g. `https://api.yourorg.org/api/v1` (build-time, must end with `/api/v1`) |
   | `NEXT_PUBLIC_AI_URL` | Public URL of your AI service, e.g. `https://api.yourorg.org:8001/api/v1` |
   | `BACKEND_URL` | **Server-side** base URL the Next.js proxies use to reach your backend, e.g. `https://api.yourorg.org` (do NOT use `localhost` here) |

   `NEXT_PUBLIC_*` values are baked into the build, so they must be set **before**
   the build runs. `BACKEND_URL` is read at runtime on the server.
5. On your backend server set `CORS_ORIGINS` to your new frontend URL.
6. Because the images and AI chat are served through Next.js server routes
   (`/api/images/...`, `/api/ai-proxy/...`), the platform must run real server
   code — **static-only** hosts (plain GitHub Pages, etc.) won't work for those
   features. Choose a platform that supports Next.js server runtime.

#### Option C — Serverless/static platforms (Netlify, Cloudflare Pages, etc.)
These can host Next.js apps with adapters (e.g. Netlify's Next.js runtime,
Cloudflare's `@cloudflare/next-on-pages`). They generally work, but server
routes (image proxy, AI chat proxy) run as serverless functions, so:
- configure the platform's Next.js adapter,
- set the same env vars as Option B,
- be aware of per-function timeouts (AI chat responses can take 30+ seconds).

> For teams without web infrastructure experience, **Option A** (everything on
> one server via Docker) is the most reliable non-Vercel deployment.

---

## 8. First run — creating the first administrator

New users who register are always created as **researcher**. Since the admin
console requires an existing admin, promote the first account directly in the
database:

1. Start the stack and open the platform. Register your first account (any role).
2. Open a shell inside the postgres container:
   ```bash
   docker compose exec postgres psql -U <POSTGRES_USER> -d <POSTGRES_DB>
   ```
3. Run:
   ```sql
   UPDATE auth.users SET role = 'admin' WHERE email = 'you@yourorg.org';
   ```
4. Log out and log back in. You now have Admin access; promote other PIs/admins
   via **Admin → Users** (role dropdown).

Role overview: `researcher` (default), `technician`, `principal_investigator`,
`admin`, `readonly` (read-only access to most modules).

---

## 9. Operations

### 9.1 Daily status
```bash
docker compose ps
curl http://localhost:8000/health
```

### 9.2 Logs
```bash
docker compose logs -f api        # backend
docker compose logs -f web        # frontend
docker compose logs -f ai-service # AI
```

### 9.3 Updating the platform
```bash
git pull origin master
docker compose up -d --build
docker compose run --rm api alembic upgrade head
```

### 9.4 Backups
- PostgreSQL: `docker compose exec postgres pg_dump -U <user> -d <db> -F c -f /tmp/backup.dump` then copy `/tmp/backup.dump` out of the container. Schedule nightly cron jobs.
- Neo4j: `neo4j-admin database dump` (see Neo4j docs).
- Qdrant: back up the `qdrant` container volume.
- Uploaded images/files: back up the volume (`STORAGE_*` location) too.
- Test restores periodically.

### 9.5 Resources / capacity
- If indexing gets slow, give postgres/neo4j more RAM in Compose.
- The AI service is the heaviest consumer when a local Ollama model is in use.

---

## 10. Security checklist

- [ ] Replace `SECRET_KEY` and all database passwords in `.env`.
- [ ] `ENVIRONMENT=production`, `DEBUG=False`.
- [ ] `CORS_ORIGINS` set to only your frontend origin(s).
- [ ] TLS/HTTPS enabled (section 7.2) for any internet-facing install.
- [ ] Only ports 443/80 open on public firewalls.
- [ ] SMTP settings configured so users can verify email / reset passwords.
- [ ] Sentinel / rotate to non-default credentials for Ollama if reachable over the network.
- [ ] Run database backups and keep an off-site copy.
- [ ] Use strong passwords: min 8 chars, upper+lower+digit+special (enforced).

---

## 11. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| API `8000` unreachable from another LAN machine | Open port 8000/3000 in the firewall; check `NEXT_PUBLIC_API_URL`. |
| "AI assistant says something went wrong" | Ollama not running (`curl localhost:11434`), model not pulled, or `OLLAMA_BASE_URL` wrong on Windows (`host.docker.internal`). |
| CORS errors in browser | `CORS_ORIGINS` in `.env` does not match the URL in the address bar. Update + restart api. |
| Images not loading | `BACKEND_URL` on the `web` container must point to the API (`http://api:8000`), not `localhost`; the Next.js proxy forwards `/api/images/...`. Edit `docker-compose.yml` and rebuild. |
| Login works but Admin tab missing | User role is not `admin`; promote via SQL (section 8) or an existing admin. |
| "Email verification required" | SMTP not configured, or verification email blocked by the recipient's server. |
| Docker won't start on Windows | Use Docker Desktop with WSL2 (or Hyper-V) integration; WSL does not need a separate install. |
| `alembic upgrade head` fails | Ensure postgres is healthy first (`docker compose ps`), then retry. |
| Slow AI responses | Local CPU-only inference is slow; use a small model (`gemma2:2b`) or an OpenAI key. |

---

## 12. References

- `README.md` — overview and quick start.
- `DEPLOYMENT.md` / `docs/deployment.md` — hosted/cloud deployment (Vercel, HF Spaces, managed DBs).
- `docs/architecture.md` — architecture and domain modules.
- `USER_MANUAL.md` — user manual for researchers.
- `AI_BEHAVIOUR.md` — rules the AI agents follow.
- `docs/testing.md`, `docs/api-reference.md` (see `docs/`) — tests and API reference.