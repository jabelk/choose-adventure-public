# Implementation Plan: Linux Hosting Setup

**Branch**: `016-linux-hosting` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/016-linux-hosting/spec.md`

## Summary

Create deployment scripts and configuration files to run the choose-your-own-adventure app on a home Linux NUC (warp-nuc). Uses systemd for service management, Caddy for reverse proxy, and a simple SSH-based deploy script. All deployment artifacts live in a `deploy/` directory in the repository.

## Technical Context

**Language/Version**: Bash (deploy scripts), INI (systemd), Caddyfile (reverse proxy)
**Primary Dependencies**: systemd, Caddy (apt package), Python 3.10+ (on NUC)
**Storage**: No new storage — app uses existing file-based storage
**Testing**: Manual testing via SSH to NUC
**Target Platform**: Debian/Ubuntu Linux (Intel NUC "warp-nuc")
**Project Type**: Infrastructure/deployment configuration
**Performance Goals**: App accessible within 30s of boot, deploy under 60s
**Constraints**: LAN-only, HTTP (no HTTPS required), SSH key access available
**Scale/Scope**: Single machine, 1-5 concurrent users

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Deployment doesn't change application behavior. Tier isolation is preserved. |
| II. Local-First | PASS | Deploying to the home NUC IS the local-first principle in action. |
| III. Iterative Simplicity | PASS | Direct uvicorn (no gunicorn), Caddy (not nginx), bash scripts (no CI/CD). Simplest viable approach. |
| IV. Archival by Design | PASS | Story data persists in the same file-based storage on the NUC. |
| V. Fun Over Perfection | PASS | Simple deploy script over complex pipelines. Skip monitoring dashboards, Docker, etc. |

**Post-design re-check**: All 5 principles PASS.

## Project Structure

### Documentation (this feature)

```text
specs/016-linux-hosting/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # N/A — no data model changes
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output
```

### Source Code (new files)

```text
deploy/
├── setup.sh             # NEW: One-time setup script (run on the NUC)
├── deploy.sh            # NEW: Repeatable deploy script (run from laptop)
├── choose-adventure.service  # NEW: systemd service unit file
├── Caddyfile            # NEW: Caddy reverse proxy config
└── env.example          # NEW: Example environment file for API keys
```

**Structure Decision**: All deployment files in a dedicated `deploy/` directory. No changes to application code. Scripts are designed to be run manually by the developer.

## File Change Map

| File | Action | Purpose |
|------|--------|---------|
| `deploy/setup.sh` | CREATE | One-time NUC setup: install Caddy, create venv, install deps, copy systemd unit, create env file, enable services |
| `deploy/deploy.sh` | CREATE | Repeatable deploy: SSH to NUC, git pull, pip install, restart service, verify |
| `deploy/choose-adventure.service` | CREATE | systemd unit file for the uvicorn app service |
| `deploy/Caddyfile` | CREATE | Caddy reverse proxy config (port 80 → localhost:8080) |
| `deploy/env.example` | CREATE | Example .env file showing required API keys |
