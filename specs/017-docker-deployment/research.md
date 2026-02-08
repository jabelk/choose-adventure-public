# Research: Docker Deployment

## Decision 1: Container Runtime — Docker Compose v2

**Decision**: Use Docker Compose v2 (the `docker compose` plugin, not standalone `docker-compose`).

**Rationale**: Docker Compose v2 is the current standard, ships with Docker Engine on Ubuntu 24.04, and is already installed on the NUC. The `docker compose` command (space, not hyphen) is the modern invocation.

**Alternatives considered**: Docker standalone, Podman (not installed on NUC).

## Decision 2: Persistent Storage — Bind Mounts (Not Named Volumes)

**Decision**: Use bind mounts to map host directories directly into containers.

**Rationale**: The app writes to `data/` and `static/images/` and `static/videos/` relative to the project root. Bind mounts let us map these to the host filesystem at known paths, making data visible and easy to back up (just `rsync` the directories). Named volumes would hide data inside Docker's internal storage, making backups harder.

**Bind mount mapping**:
- `./data:/app/data` — stories, progress, profiles, photos
- `./static/images:/app/static/images` — generated scene images
- `./static/videos:/app/static/videos` — generated videos

**Alternatives considered**: Named Docker volumes (data hidden in /var/lib/docker/volumes, harder to inspect/backup).

## Decision 3: Base Image — python:3.12-slim

**Decision**: Use `python:3.12-slim` as the base Docker image.

**Rationale**: Matches the NUC's Python 3.12. The slim variant is ~150MB vs ~900MB for the full image, reducing build time and disk usage. It includes pip and venv support. No compiled dependencies in requirements.txt need build tools (Pillow has prebuilt wheels for slim).

**Alternatives considered**: python:3.12-alpine (smaller but musl libc can cause issues with some Python packages), python:3.12 full (unnecessarily large).

## Decision 4: Reverse Proxy — Caddy Container

**Decision**: Use the official `caddy:2-alpine` Docker image as the reverse proxy container.

**Rationale**: Consistent with the Caddyfile already created in feature 016. Caddy is simple to configure (4-line config), auto-handles HTTP, and the alpine image is tiny (~40MB). No changes needed to the existing Caddyfile except pointing to the app container hostname instead of localhost.

**Alternatives considered**: Nginx (more complex config, no benefit for this use case), Traefik (overkill for a two-container setup).

## Decision 5: Deploy Strategy — Rebuild and Recreate

**Decision**: Deploy by SSHing to NUC, running `git pull`, then `docker compose up --build -d`.

**Rationale**: Docker Compose handles the rebuild-and-replace cycle natively. `--build` rebuilds the app image with the new code, `-d` restarts in detached mode. The old containers continue serving until the new ones are ready. This is the simplest approach with zero-config rolling updates.

**Error handling**: If the build fails, the old containers keep running (Docker Compose doesn't tear down running containers on build failure).

## Decision 6: App Directory on NUC — /home/jabelk/choose-adventure

**Decision**: Clone the repo to `/home/jabelk/choose-adventure` (user's home directory) instead of `/opt/choose-adventure`.

**Rationale**: The SSH user is `jabelk` with key-based auth. Placing the repo in the user's home directory avoids all sudo/permission issues for git pull, docker compose commands, and file ownership. The previous bare-metal approach needed `/opt/` for the systemd service user, but Docker eliminates that requirement. The `jabelk` user just needs to be in the `docker` group.

**Alternatives considered**: `/opt/choose-adventure` (requires sudo for git operations, more complex permissions).

## Decision 7: Environment File — .env in Project Root

**Decision**: Store the `.env` file in the project root directory on the NUC (not `/etc/default/`).

**Rationale**: Docker Compose natively reads `.env` files from the project directory. The `env_file` directive in docker-compose.yml can reference it directly. This is simpler than the `/etc/default/` approach used in bare-metal deployment. The `.env` file is already in `.gitignore`.

**Alternatives considered**: `/etc/default/choose-adventure.env` (requires sudo, not the Docker convention).

## Decision 8: Replacing Bare-Metal Deploy Files

**Decision**: Replace the contents of `deploy/` entirely. Remove systemd service file, bare-metal setup.sh, and bare-metal deploy.sh. Replace with Docker-specific files.

**Rationale**: The bare-metal approach (systemd + Caddy installed via apt) is fully superseded by Docker Compose. Keeping both approaches would be confusing. The Caddyfile can be reused with minor modification.

**Files to remove**: `deploy/choose-adventure.service`, `deploy/setup.sh`, `deploy/deploy.sh`
**Files to keep/modify**: `deploy/Caddyfile` (update proxy target), `deploy/env.example` (keep as-is)
**Files to create**: `Dockerfile`, `docker-compose.yml`, `deploy/setup.sh` (new Docker version), `deploy/deploy.sh` (new Docker version), `.dockerignore`
