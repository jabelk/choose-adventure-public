# Tasks: Linux Hosting Setup

**Input**: Design documents from `/specs/016-linux-hosting/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: No automated tests. Manual testing via SSH to NUC per quickstart.md.

**Organization**: Tasks are grouped by user story.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the deploy directory and shared configuration files.

- [X] T001 [P] Create deploy/choose-adventure.service — systemd unit file for the uvicorn app. Type=exec, User/Group from setup, WorkingDirectory=/opt/choose-adventure, EnvironmentFile=/etc/default/choose-adventure.env, ExecStart using venv/bin/python with uvicorn, Restart=on-failure with rate limits, StandardOutput/Error to journal.
- [X] T002 [P] Create deploy/Caddyfile — Caddy reverse proxy config. Listen on port 80 (`:80`), reverse_proxy to localhost:8080. Keep it minimal.
- [X] T003 [P] Create deploy/env.example — example environment file showing all possible API key variables with placeholder values and comments.

---

## Phase 2: User Story 1 — Deploy and Run on the NUC (Priority: P1)

**Goal**: One-time setup script that installs everything and starts the service.

- [X] T004 [US1] Create deploy/setup.sh — one-time setup script that: (1) checks prerequisites (python3, pip, git), (2) creates venv and installs deps from requirements.txt, (3) copies systemd unit file to /etc/systemd/system/, (4) creates env file at /etc/default/ if it doesn't exist (from env.example), (5) installs Caddy via apt if not present, (6) copies Caddyfile to /etc/caddy/, (7) reloads systemd, enables and starts both services. Must be run with sudo. Include clear step-by-step output.
- [X] T005 [US1] Verify setup script is syntactically valid — run bash -n on the script and verify it handles all error cases.

---

## Phase 3: User Story 2 — Reverse Proxy with Clean URLs (Priority: P2)

**Goal**: Caddy serves the app on port 80.

- [X] T006 [US2] Verify Caddyfile configuration — the Caddyfile from T002 handles this. Verify it includes proper proxy headers (Host, X-Real-IP, X-Forwarded-For).

---

## Phase 4: User Story 3 — Simple Deployment Workflow (Priority: P3)

**Goal**: Single-command deploy from laptop.

- [X] T007 [US3] Create deploy/deploy.sh — repeatable deploy script run from the developer's laptop. Uses SSH to: (1) cd to app directory, (2) git pull origin main, (3) venv/bin/pip install -r requirements.txt, (4) sudo systemctl restart choose-adventure. Includes error handling (set -euo pipefail), step numbering, and final status check. Configurable NUC_HOST variable at top.
- [X] T008 [US3] Verify deploy script is syntactically valid — run bash -n on the script.

---

## Phase 5: Polish

- [X] T009 Add deploy/ directory to .gitignore exclusions — ensure deploy/*.sh and deploy/ files are NOT ignored by any gitignore rules.
- [X] T010 Verify all deploy files are complete and consistent — cross-check service file paths match setup script paths, env file paths match service EnvironmentFile, Caddyfile proxy_pass port matches service ExecStart port.

---

## Dependencies

- **Phase 1**: No dependencies — config files can be created independently
- **Phase 2 (US1)**: Depends on Phase 1 (setup.sh references service file, Caddyfile, env.example)
- **Phase 3 (US2)**: Depends on Phase 1 (Caddyfile must exist)
- **Phase 4 (US3)**: Independent — deploy.sh only needs SSH access
- **Phase 5**: Depends on all previous phases

## Notes

- All files are NEW — no existing files modified
- Scripts must be executable (chmod +x)
- Setup script requires sudo — deploy script uses SSH
- The NUC hostname/IP is configurable at the top of deploy.sh
- Commit after all phases complete (single commit for all deploy files)
