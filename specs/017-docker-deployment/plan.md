# Implementation Plan: Docker Deployment

**Branch**: `017-docker-deployment` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/017-docker-deployment/spec.md`

## Summary

Replace the bare-metal systemd/Caddy deployment from feature 016 with a Docker Compose setup. Two containers (Python app + Caddy reverse proxy) with bind-mounted persistent storage for all user data. One-command setup and deploy via SSH from the developer's laptop.

## Technical Context

**Language/Version**: Python 3.12 (matching NUC), Bash for scripts
**Primary Dependencies**: Docker Compose v2, Caddy 2 (alpine image), python:3.12-slim base
**Storage**: Filesystem — bind mounts for `data/` and `static/images/` and `static/videos/`
**Testing**: Manual testing via SSH to NUC (per spec)
**Target Platform**: Ubuntu 24.04 (NUC "warp-nuc"), Docker pre-installed
**Project Type**: Deployment configuration (no app code changes)
**Performance Goals**: App accessible within 3 minutes of setup, deploys under 2 minutes
**Constraints**: Two containers max, single docker-compose.yml, no sudo required
**Scale/Scope**: Single NUC, 1-5 LAN users, ~200MB app image

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | No changes to app code or tier routing. Containers serve the same app. |
| II. Local-First | PASS | Docker runs on the NUC, self-hosted. No cloud dependencies for serving. |
| III. Iterative Simplicity | PASS | Docker Compose is simpler than systemd + manual Caddy install. Two containers, one config file. |
| IV. Archival by Design | PASS | Bind mounts ensure all story/image data persists on the NUC filesystem, visible and backupable. |
| V. Fun Over Perfection | PASS | Simple setup — no K8s, no CI/CD, no container registry. Just `docker compose up`. |

## Project Structure

### Documentation (this feature)

```text
specs/017-docker-deployment/
├── plan.md              # This file
├── research.md          # Technology decisions
├── quickstart.md        # Setup and deploy instructions
└── tasks.md             # Task breakdown
```

### Source Code (repository root)

```text
choose-adventure/
├── Dockerfile                    # NEW — app container image definition
├── docker-compose.yml            # NEW — orchestration config (app + caddy)
├── .dockerignore                 # NEW — exclude unnecessary files from build context
├── deploy/
│   ├── Caddyfile                 # MODIFIED — proxy target from localhost to app container
│   ├── env.example               # KEPT — reference for API key configuration
│   ├── setup.sh                  # REPLACED — Docker-based one-time setup
│   └── deploy.sh                 # REPLACED — Docker-based deploy from laptop
├── app/                          # UNCHANGED
├── templates/                    # UNCHANGED
├── static/                       # UNCHANGED
│   ├── images/                   # Bind-mounted for persistence
│   └── videos/                   # Bind-mounted for persistence
├── data/                         # Bind-mounted for persistence
│   ├── stories/
│   ├── progress/
│   ├── profiles/
│   └── photos/
└── requirements.txt              # UNCHANGED
```

**Structure Decision**: Deployment config files (Dockerfile, docker-compose.yml) live at project root per Docker convention. Scripts stay in `deploy/`. No app code changes needed.

## Complexity Tracking

No constitution violations. No complexity justifications needed.
