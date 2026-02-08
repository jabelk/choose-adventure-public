# Feature Specification: Linux Hosting Setup

**Feature Branch**: `016-linux-hosting`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Linux Hosting Setup - Deploy the app to a home Linux box (Intel NUC) with systemd service, reverse proxy, and LAN access. User has SSH keys already configured."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy and Run on the NUC (Priority: P1)

The developer clones the repository on their Linux NUC (warp-nuc), runs a setup script, and the app starts automatically as a background service. The app is accessible from any device on the home LAN by navigating to the NUC's IP address in a browser. The service restarts automatically if it crashes or after a system reboot.

**Why this priority**: This is the core deployment goal — getting the app running persistently on the NUC so the family can use it anytime without the developer manually starting it.

**Independent Test**: SSH into the NUC, run the setup, then open the app from a phone or tablet on the same network. Reboot the NUC and verify the app comes back up automatically.

**Acceptance Scenarios**:

1. **Given** the repo is cloned on the NUC and the setup script has been run, **When** a user on the LAN opens a browser to `http://<NUC_IP>`, **Then** the app's landing page loads.
2. **Given** the app is running as a service, **When** the NUC is rebooted, **Then** the app starts automatically within 30 seconds of boot completing.
3. **Given** the app process crashes unexpectedly, **When** the service manager detects the failure, **Then** it restarts the app automatically within 10 seconds.
4. **Given** the app is running, **When** the developer checks the service status, **Then** they can see whether the app is running, how long it has been up, and recent log output.

---

### User Story 2 - Reverse Proxy with Clean URLs (Priority: P2)

The app is served behind a reverse proxy so that users access it on port 80 (standard HTTP) rather than the raw application port (8080). This provides cleaner URLs and allows future flexibility (e.g., serving multiple apps, adding HTTPS later).

**Why this priority**: Quality-of-life improvement. Port 80 means users don't need to remember `:8080` in URLs. Also sets the foundation for HTTPS if ever needed for PWA service workers on the NUC.

**Independent Test**: Navigate to `http://<NUC_IP>/` (no port) and verify the app loads. Navigate to `http://<NUC_IP>:8080/` and verify the raw app also still works (for debugging).

**Acceptance Scenarios**:

1. **Given** the reverse proxy is configured, **When** a user navigates to `http://<NUC_IP>/`, **Then** the app loads on port 80 without needing to specify a port.
2. **Given** the reverse proxy is running, **When** any page or static asset is requested, **Then** it is served correctly with proper content types.
3. **Given** the reverse proxy is configured, **When** checking the proxy status, **Then** it is running as a service and auto-starts on boot.

---

### User Story 3 - Simple Deployment Workflow (Priority: P3)

The developer can deploy code updates from their laptop to the NUC with a single command. After pushing changes to the repo, they run a deploy script (or SSH command) that pulls the latest code and restarts the service. No manual steps on the NUC are required.

**Why this priority**: Reduces friction for iterating on the app. Without this, every update requires SSH-ing in and running multiple commands manually.

**Independent Test**: Make a code change on the laptop, push to GitHub, run the deploy command, and verify the change is live on the NUC within 60 seconds.

**Acceptance Scenarios**:

1. **Given** a new commit has been pushed to the main branch, **When** the developer runs the deploy command from their laptop, **Then** the NUC pulls the latest code and restarts the service.
2. **Given** a deploy is in progress, **When** the service restarts, **Then** the downtime is less than 10 seconds.
3. **Given** the deploy script encounters an error (e.g., git pull fails), **When** the error occurs, **Then** the currently running version continues to serve without interruption.

---

### Edge Cases

- What happens if the NUC's IP address changes (DHCP)? The deploy script and documentation should note the IP. Users are advised to configure a static IP or DHCP reservation for the NUC.
- What happens if API keys (Claude, OpenAI, etc.) are not configured on the NUC? The app starts but story generation fails gracefully with user-friendly error messages (existing behavior). The setup script should prompt for or document API key configuration.
- What happens if the deploy script is run while someone is actively using the app? The service restarts briefly (< 10 seconds downtime). In-progress stories are not affected since they are persisted to disk.
- What happens if Python or pip is not installed on the NUC? The setup script checks for prerequisites and provides clear error messages with installation instructions.
- What happens if the NUC runs out of disk space (from generated images)? The app continues to function for reading/browsing. New image generation fails with existing error handling. Monitoring disk usage is out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A setup script MUST install all application dependencies on the NUC (Python packages, virtual environment) and configure the app as a persistent background service.
- **FR-002**: The app MUST start automatically when the NUC boots, without manual intervention.
- **FR-003**: The app MUST restart automatically if it crashes or exits unexpectedly.
- **FR-004**: The app MUST be accessible from any device on the home LAN via the NUC's IP address on port 80.
- **FR-005**: A reverse proxy MUST forward port 80 traffic to the application's internal port.
- **FR-006**: The reverse proxy MUST pass through all request headers and support WebSocket connections (for future use).
- **FR-007**: A deploy script MUST allow the developer to update the running app from their laptop with a single command.
- **FR-008**: The deploy script MUST pull the latest code from the repository and restart the application service.
- **FR-009**: The deploy script MUST handle errors gracefully — a failed deploy MUST NOT take down the currently running app.
- **FR-010**: Application logs MUST be accessible via standard system logging tools.
- **FR-011**: API keys and environment configuration MUST be stored in a configuration file on the NUC, not in the repository.
- **FR-012**: The setup script MUST provide clear output indicating success or failure of each step.
- **FR-013**: All deployment scripts and configuration files MUST be included in the repository under a `deploy/` directory.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The app is accessible from a phone on the home LAN within 5 minutes of running the setup script on a fresh NUC clone.
- **SC-002**: After a NUC reboot, the app is accessible within 30 seconds without manual intervention.
- **SC-003**: A code deploy from the developer's laptop takes less than 60 seconds from command to live.
- **SC-004**: The app runs continuously for 7 days without manual restarts (auto-recovery from crashes does not count as manual).
- **SC-005**: All deployment artifacts (scripts, config files, documentation) are contained within the repository — no external dependencies beyond the NUC's base OS packages.

## Assumptions

- The NUC runs a Debian/Ubuntu-based Linux distribution with systemd.
- The developer has SSH key access configured from their laptop to the NUC (confirmed by user).
- The NUC has Python 3.10+ available or installable via the system package manager.
- The NUC has internet access for cloning the repo and installing pip packages (API calls already require internet).
- The NUC's hostname is "warp-nuc" (as mentioned in the constitution).
- Port 80 is available on the NUC (no other web server running).
- The app will be the only application served by the reverse proxy (no multi-site config needed).
- HTTPS is not required for initial deployment (LAN-only access, PWA uses Chrome flag workaround).

## Out of Scope

- HTTPS/TLS certificate setup (can be added later if needed for PWA)
- Docker containerization (unnecessary complexity for a single personal app)
- CI/CD pipeline (deploy script is sufficient for a one-person project)
- Monitoring, alerting, or health check dashboards
- Backup automation for story data (manual rsync or similar is sufficient)
- Multi-machine deployment or load balancing
- DNS configuration or custom domain names
