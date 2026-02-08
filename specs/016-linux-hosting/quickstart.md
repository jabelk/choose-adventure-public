# Quickstart: Linux Hosting Setup

## Prerequisites

- Linux NUC (warp-nuc) with Debian/Ubuntu, reachable via SSH
- SSH key access configured from developer laptop to NUC
- Internet access on the NUC (for apt packages, pip install, GitHub clone)

## Initial Setup (Run Once on the NUC)

### Step 1: Clone and Setup
1. SSH into the NUC: `ssh warp-nuc`
2. Clone the repo: `git clone https://github.com/jabelk/choose-adventure.git /opt/choose-adventure`
3. Run the setup script: `cd /opt/choose-adventure && sudo bash deploy/setup.sh`
4. Expected: Script completes with all steps showing success

### Step 2: Configure API Keys
1. Edit the environment file: `sudo nano /etc/default/choose-adventure.env`
2. Add your API keys (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)
3. Restart the service: `sudo systemctl restart choose-adventure`
4. Expected: Service starts with configured API keys

### Step 3: Verify Service Running
1. Check service status: `systemctl status choose-adventure`
2. Expected: Active (running), no errors in recent logs

### Step 4: Verify LAN Access
1. From a phone/tablet on the same network, open `http://<NUC_IP>/`
2. Expected: App landing page loads

### Step 5: Verify Port 80 (Caddy)
1. Navigate to `http://<NUC_IP>/` (no port number)
2. Expected: App loads via Caddy reverse proxy on port 80

### Step 6: Verify Auto-Restart on Crash
1. Kill the app process: `sudo systemctl kill choose-adventure`
2. Wait 10 seconds
3. Check status: `systemctl status choose-adventure`
4. Expected: Service is active again (systemd restarted it)

### Step 7: Verify Auto-Start on Boot
1. Reboot the NUC: `sudo reboot`
2. Wait 30 seconds
3. Open `http://<NUC_IP>/` from another device
4. Expected: App is accessible

## Deploying Updates (Repeatable)

### Step 8: Deploy from Laptop
1. Push changes to main branch on GitHub
2. From laptop, run: `bash deploy/deploy.sh`
3. Expected: Script pulls code, installs deps, restarts service, shows success

### Step 9: Verify Deploy
1. Open the app in a browser and confirm the change is live
2. Expected: New changes visible immediately
