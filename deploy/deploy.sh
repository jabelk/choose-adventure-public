#!/usr/bin/env bash
# Choose Your Own Adventure - Deploy updates to NUC via Docker
# Run this FROM YOUR LAPTOP: ./deploy/deploy.sh
# Prerequisites: NUC already set up via setup.sh

set -euo pipefail

NUC_HOST="jabelk@warp-nuc"
APP_DIR="choose-adventure"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() { echo -e "\n${GREEN}[Step $1]${NC} $2"; }
warn() { echo -e "${YELLOW}WARNING:${NC} $1"; }
fail() { echo -e "${RED}FAILED:${NC} $1"; exit 1; }

echo "========================================="
echo " Choose Your Own Adventure - Deploy"
echo "========================================="
echo "Target: $NUC_HOST"

# --- Step 1: Pull latest code ---
step 1 "Pulling latest code..."

ssh "$NUC_HOST" "cd ~/$APP_DIR && git pull origin main" || fail "git pull failed. Check repo state on NUC."
echo "  Code updated"

# --- Step 2: Rebuild and restart containers ---
step 2 "Rebuilding and restarting containers..."

ssh "$NUC_HOST" "cd ~/$APP_DIR && docker compose up --build -d" || fail "Docker compose failed. Old containers may still be running."
echo "  Containers restarted"

# --- Step 3: Verify app is responding ---
step 3 "Verifying app is responding..."

sleep 5
HTTP_CODE=$(ssh "$NUC_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost/" || echo "000")

if [[ "$HTTP_CODE" == "200" ]]; then
    echo -e "  ${GREEN}Deploy successful! (HTTP $HTTP_CODE)${NC}"
else
    warn "App returned HTTP $HTTP_CODE. Check logs:"
    echo "  ssh $NUC_HOST \"cd ~/$APP_DIR && docker compose logs --tail=20 app\""
fi

# --- Step 4: Show status ---
step 4 "Container status:"

ssh "$NUC_HOST" "cd ~/$APP_DIR && docker compose ps"

echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
