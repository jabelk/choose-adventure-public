# Tasks: Docker Deployment

**Input**: Design documents from `/specs/017-docker-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: No automated tests. Manual testing via SSH to NUC per quickstart.md.

**Organization**: Tasks are grouped by user story.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create Docker configuration files and replace bare-metal deploy files.

- [X] T001 [P] Create Dockerfile at project root — python:3.12-slim base, copy requirements.txt and install deps first (for layer caching), then copy app/ templates/ static/ (excluding images/ and videos/ which are bind-mounted), expose port 8080, CMD uvicorn with 2 workers on 0.0.0.0:8080.
- [X] T002 [P] Create .dockerignore at project root — exclude venv/, data/, static/images/, static/videos/, .git/, __pycache__/, *.pyc, .env, .specify/, specs/, .claude/, docs/, *.md (except requirements.txt).
- [X] T003 [P] Create docker-compose.yml at project root — two services: (1) app service built from Dockerfile, env_file .env, bind mounts for ./data:/app/data, ./static/images:/app/static/images, ./static/videos:/app/static/videos, restart unless-stopped; (2) caddy service using caddy:2-alpine image, ports 80:80, volume mount deploy/Caddyfile to /etc/caddy/Caddyfile, depends_on app, restart unless-stopped. Internal network connects them.
- [X] T004 Update deploy/Caddyfile — change reverse_proxy target from localhost:8080 to app:8080 (Docker service name).

---

## Phase 2: User Story 1 & 4 — Initial Setup + Persistent Data (Priority: P1)

**Goal**: One-time setup script that clones, configures, and starts containers with persistent storage.

- [X] T005 [US1] Replace deploy/setup.sh — new Docker-based one-time setup script run FROM the developer's laptop. Uses SSH (jabelk@warp-nuc) to: (1) check Docker is available, (2) clone repo to ~/choose-adventure if not present, (3) copy deploy/env.example to .env if .env doesn't exist, (4) prompt user to edit .env for API keys, (5) create data/ and static/images/ and static/videos/ directories, (6) run docker compose up --build -d, (7) wait and verify app is responding on port 80. Include set -euo pipefail, colored step output, NUC_HOST variable at top.
- [X] T006 [US1] Verify setup.sh is syntactically valid — run bash -n on the script.

**Checkpoint**: After setup.sh runs on NUC, app should be accessible at http://192.168.4.152/ with persistent data directories created.

---

## Phase 3: User Story 2 — Reverse Proxy (Priority: P2)

**Goal**: Caddy container serves the app on port 80.

- [X] T007 [US2] Verify Caddyfile and docker-compose.yml are consistent — Caddy container maps port 80:80, Caddyfile proxies to app:8080, proper headers included.

---

## Phase 4: User Story 3 — One-Command Deploy (Priority: P3)

**Goal**: Single-command deploy from the developer's laptop.

- [X] T008 [US3] Replace deploy/deploy.sh — new Docker-based deploy script run from the developer's laptop. Uses SSH (jabelk@warp-nuc) to: (1) cd ~/choose-adventure, (2) git pull origin main, (3) docker compose up --build -d, (4) wait 5 seconds, (5) verify app is responding. Include set -euo pipefail, colored step output, NUC_HOST variable, error handling so failed build doesn't take down running app.
- [X] T009 [US3] Verify deploy.sh is syntactically valid — run bash -n on the script.

---

## Phase 5: Polish

- [X] T010 Remove deploy/choose-adventure.service — systemd unit file is no longer needed with Docker.
- [X] T011 Verify all deploy files are complete and consistent — cross-check docker-compose.yml bind mounts match app runtime directories, Caddyfile proxy target matches compose service name, Dockerfile EXPOSE matches uvicorn port, env_file path in compose matches setup.sh creation path.
- [X] T012 Verify .dockerignore excludes the right files and Dockerfile builds successfully — run a local docker build test.

---

## Dependencies

- **Phase 1**: No dependencies — config files can be created independently (all [P])
- **Phase 2 (US1/US4)**: Depends on Phase 1 (setup.sh references docker-compose.yml and Caddyfile)
- **Phase 3 (US2)**: Depends on Phase 1 (Caddyfile and compose must exist)
- **Phase 4 (US3)**: Independent — deploy.sh only needs SSH access and existing compose setup
- **Phase 5**: Depends on all previous phases

## Notes

- deploy/setup.sh and deploy/deploy.sh are REPLACED (not modified) — entirely new scripts
- deploy/choose-adventure.service is DELETED
- deploy/Caddyfile is MODIFIED (proxy target only)
- deploy/env.example is KEPT unchanged
- Dockerfile, docker-compose.yml, .dockerignore are NEW files at project root
- Scripts must be executable (chmod +x)
- Commit after all phases complete (single commit for all deploy files)
