# Quickstart: Docker Deployment

## Prerequisites

- NUC (warp-nuc) running Ubuntu 24.04 with Docker installed
- SSH key access: `ssh jabelk@warp-nuc` works without password
- Git repo accessible from NUC (GitHub SSH or HTTPS)

## First-Time Setup (on NUC)

```bash
# From your laptop:
ssh jabelk@warp-nuc

# On the NUC:
cd ~
git clone <repo-url> choose-adventure
cd choose-adventure

# Create environment file with API keys
cp deploy/env.example .env
nano .env  # Add your API keys

# Build and start
docker compose up --build -d

# Verify
docker compose ps
curl http://localhost/
```

App should be accessible at `http://192.168.4.152/` from any LAN device.

## Deploy Updates (from laptop)

```bash
# Single command from your laptop:
./deploy/deploy.sh
```

Or manually:
```bash
ssh jabelk@warp-nuc "cd ~/choose-adventure && git pull && docker compose up --build -d"
```

## Common Operations

```bash
# View logs
ssh jabelk@warp-nuc "cd ~/choose-adventure && docker compose logs -f app"

# Check status
ssh jabelk@warp-nuc "cd ~/choose-adventure && docker compose ps"

# Restart
ssh jabelk@warp-nuc "cd ~/choose-adventure && docker compose restart"

# Stop everything
ssh jabelk@warp-nuc "cd ~/choose-adventure && docker compose down"
```

## Verify Persistent Data

1. Create a story via the web interface
2. Run a deploy: `./deploy/deploy.sh`
3. Check the story still appears in the gallery
4. On the NUC, data is at `~/choose-adventure/data/` and images at `~/choose-adventure/static/images/`

## Manual Testing Checklist

- [ ] App loads at `http://192.168.4.152/`
- [ ] Kids tier loads at `http://192.168.4.152/kids/`
- [ ] Story creation works (requires API keys)
- [ ] Images generate and display
- [ ] Gallery shows completed stories
- [ ] Deploy from laptop succeeds
- [ ] Data persists after deploy
- [ ] App recovers after NUC reboot
