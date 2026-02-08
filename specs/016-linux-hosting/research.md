# Research: Linux Hosting Setup

## Decision 1: App Server — Direct Uvicorn (No Gunicorn)

**Decision**: Use uvicorn directly with `--workers 2`.

**Rationale**: For a home LAN with 1-5 concurrent users, gunicorn adds unnecessary complexity. Uvicorn supports multiple workers natively. The app is already developed and tested with uvicorn.

**Alternatives considered**: Gunicorn + uvicorn workers (overkill for this scale).

## Decision 2: Reverse Proxy — Caddy

**Decision**: Use Caddy as the reverse proxy.

**Rationale**: Caddy has dramatically simpler configuration than nginx (4 lines vs 20+). It auto-handles HTTPS if ever needed. Available in Debian/Ubuntu repos via `apt install caddy`. Perfect for a low-maintenance home server.

**Alternatives considered**: Nginx (more complex config, manual HTTPS management).

## Decision 3: Service Manager — systemd

**Decision**: Use systemd with `Restart=on-failure` and rate limits.

**Rationale**: systemd is the standard on Debian/Ubuntu. Provides auto-start on boot, crash recovery, and journald logging out of the box.

**Key settings**: `RestartSec=5s`, `StartLimitBurst=5`, `StartLimitInterval=300s` to prevent infinite restart loops.

## Decision 4: Environment Configuration — /etc/default/

**Decision**: Store API keys in `/etc/default/choose-adventure.env`, loaded by systemd's `EnvironmentFile` directive.

**Rationale**: Keeps secrets out of the repo. Standard Linux location for service config. Restrictive file permissions (640, root:appuser).

## Decision 5: Deploy Script — SSH + git pull + systemctl restart

**Decision**: Simple bash script run from the developer's laptop that SSHes to the NUC, pulls code, installs deps, and restarts the service.

**Rationale**: Simplest approach for a single developer. No CI/CD pipeline needed. Uses existing SSH key access.

**Error handling**: `set -euo pipefail`, numbered steps, verify service is running after restart.

## Decision 6: App User — Dedicated Service Account

**Decision**: Run the app as a dedicated `adventure` user (not root).

**Rationale**: Security best practice. Limits damage if the app is compromised. The service account owns the app directory but has no sudo access.

**Sudoers exception**: Allow the user's SSH account to restart the service via `sudoers` without password prompt.
