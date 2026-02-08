#!/usr/bin/env bash
# Choose Your Own Adventure - One-time Docker setup on NUC
# Run this FROM YOUR LAPTOP: ./deploy/setup.sh
# Prerequisites: SSH key access to NUC (jabelk@warp-nuc)

set -euo pipefail

NUC_HOST="jabelk@warp-nuc"
APP_DIR="choose-adventure"
REPO_URL="git@github.com:jabelk/choose-adventure.git"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

step() { echo -e "\n${GREEN}[Step $1]${NC} $2"; }
warn() { echo -e "${YELLOW}WARNING:${NC} $1"; }
fail() { echo -e "${RED}FAILED:${NC} $1"; exit 1; }

echo "========================================="
echo " Choose Your Own Adventure - NUC Setup"
echo "========================================="
echo "Target: $NUC_HOST"
echo ""

# --- Step 1: Verify SSH connectivity ---
step 1 "Verifying SSH connectivity..."

ssh -o ConnectTimeout=5 "$NUC_HOST" "echo 'SSH connection OK'" || fail "Cannot connect to $NUC_HOST. Check SSH keys and network."
echo "  Connected to NUC"

# --- Step 2: Check Docker is available ---
step 2 "Checking Docker on NUC..."

ssh "$NUC_HOST" "docker --version && docker compose version" || fail "Docker or Docker Compose not found on NUC."
echo "  Docker is ready"

# --- Step 3: Clone the repo if not present ---
step 3 "Setting up repository..."

ssh "$NUC_HOST" bash -s <<REMOTE_SCRIPT
set -euo pipefail
if [[ -d ~/$APP_DIR/.git ]]; then
    echo "  Repository already exists at ~/$APP_DIR"
    cd ~/$APP_DIR
    git pull origin main
else
    echo "  Cloning repository..."
    cd ~
    git clone $REPO_URL $APP_DIR
    echo "  Cloned to ~/$APP_DIR"
fi
REMOTE_SCRIPT

# --- Step 4: Create .env file if not present ---
step 4 "Checking environment file..."

ENV_EXISTS=$(ssh "$NUC_HOST" "[[ -f ~/$APP_DIR/.env ]] && echo 'yes' || echo 'no'")
if [[ "$ENV_EXISTS" == "no" ]]; then
    ssh "$NUC_HOST" "cp ~/$APP_DIR/deploy/env.example ~/$APP_DIR/.env"
    echo "  Created .env from template"
    warn "You MUST edit the .env file with your API keys:"
    echo "  ssh $NUC_HOST \"nano ~/$APP_DIR/.env\""
    echo ""
    read -p "  Press Enter after editing .env (or Ctrl+C to abort)..."
else
    echo "  .env already exists (not overwriting)"
fi

# --- Step 5: Create persistent data directories ---
step 5 "Creating data directories..."

ssh "$NUC_HOST" bash -s <<'REMOTE_SCRIPT'
set -euo pipefail
cd ~/choose-adventure
mkdir -p data/stories data/progress data/profiles data/photos
mkdir -p static/images static/videos
echo "  Directories ready"
REMOTE_SCRIPT

# --- Step 6: Build and start containers ---
step 6 "Building and starting containers..."

ssh "$NUC_HOST" "cd ~/$APP_DIR && docker compose up --build -d"
echo "  Containers started"

# --- Step 7: Verify the app is running ---
step 7 "Verifying app is responding..."

sleep 5
HTTP_CODE=$(ssh "$NUC_HOST" "curl -s -o /dev/null -w '%{http_code}' http://localhost/" || echo "000")

if [[ "$HTTP_CODE" == "200" ]]; then
    echo -e "  ${GREEN}App is running! (HTTP $HTTP_CODE)${NC}"
else
    warn "App returned HTTP $HTTP_CODE. Check logs: ssh $NUC_HOST \"cd ~/$APP_DIR && docker compose logs app\""
fi

# --- Done ---
echo ""
echo "========================================="
echo -e " ${GREEN}Setup complete!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Edit API keys:  ssh $NUC_HOST \"nano ~/$APP_DIR/.env\""
echo "  2. Restart app:    ssh $NUC_HOST \"cd ~/$APP_DIR && docker compose restart\""
echo "  3. View logs:      ssh $NUC_HOST \"cd ~/$APP_DIR && docker compose logs -f app\""
echo "  4. Check status:   ssh $NUC_HOST \"cd ~/$APP_DIR && docker compose ps\""
echo ""
LAN_IP=$(ssh "$NUC_HOST" "hostname -I | awk '{print \$1}'" 2>/dev/null || echo "192.168.4.152")
echo "  App URL: http://$LAN_IP/"
echo ""
