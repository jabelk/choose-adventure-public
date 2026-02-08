# Feature Specification: Docker Deployment

**Feature Branch**: `017-docker-deployment`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Docker Deployment - Replace bare-metal systemd/Caddy deployment with Docker Compose setup for the NUC. Two containers (app + Caddy), persistent storage for stories/images/profiles, environment file for API keys, one-command deploy from laptop."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Initial Setup and Run (Priority: P1)

The developer clones the repository on the NUC, creates an environment file with API keys, and runs a single setup command. The app starts in containers and is accessible from any device on the home LAN by navigating to the NUC's IP address in a browser. The containers restart automatically after a system reboot or if they crash.

**Why this priority**: This is the core deployment goal — getting the app running in containers on the NUC so the family can use it without the developer manually managing processes.

**Independent Test**: SSH into the NUC, clone the repo, run the setup command, then open the app from a phone on the same network. Reboot the NUC and verify the app comes back up automatically.

**Acceptance Scenarios**:

1. **Given** the repo is cloned on the NUC and the environment file is configured, **When** the developer runs the setup command, **Then** the app is accessible at `http://192.168.4.152/` within 3 minutes.
2. **Given** the app is running in containers, **When** the NUC is rebooted, **Then** the containers start automatically and the app is accessible within 60 seconds of boot completing.
3. **Given** the app container crashes unexpectedly, **When** the container runtime detects the failure, **Then** it restarts the container automatically within 15 seconds.
4. **Given** the app is running, **When** the developer checks the container status, **Then** they can see whether containers are running, how long they have been up, and recent log output.

---

### User Story 2 - Reverse Proxy with Clean URLs (Priority: P2)

The app is served behind a reverse proxy container so that users access it on port 80 (standard HTTP) rather than the raw application port. This provides cleaner URLs and allows future flexibility.

**Why this priority**: Quality-of-life improvement. Port 80 means users don't need to remember a port number in URLs.

**Independent Test**: Navigate to `http://192.168.4.152/` (no port) and verify the app loads correctly including all pages, images, and static assets.

**Acceptance Scenarios**:

1. **Given** the reverse proxy container is running, **When** a user navigates to `http://192.168.4.152/`, **Then** the app loads on port 80 without needing to specify a port.
2. **Given** the reverse proxy is running, **When** any page or static asset is requested, **Then** it is served correctly with proper content types.
3. **Given** the reverse proxy is configured, **When** checking its status, **Then** it is running and auto-starts with the other containers.

---

### User Story 3 - One-Command Deploy from Laptop (Priority: P3)

The developer can deploy code updates from their laptop to the NUC with a single command. After pushing changes to the repository, they run a deploy script that pulls the latest code on the NUC, rebuilds the app container, and restarts services. No manual steps on the NUC are required.

**Why this priority**: Reduces friction for iterating on the app. Without this, every update requires SSH-ing in and running multiple commands manually.

**Independent Test**: Make a code change on the laptop, push to GitHub, run the deploy command, and verify the change is live on the NUC within 2 minutes.

**Acceptance Scenarios**:

1. **Given** a new commit has been pushed to the main branch, **When** the developer runs the deploy command from their laptop, **Then** the NUC pulls the latest code, rebuilds the container, and restarts the service.
2. **Given** a deploy is in progress, **When** the container rebuilds and restarts, **Then** the downtime is less than 30 seconds.
3. **Given** the deploy script encounters an error (e.g., git pull fails), **When** the error occurs, **Then** the currently running version continues to serve without interruption and the developer sees a clear error message.

---

### User Story 4 - Persistent Data Across Deploys (Priority: P1)

All user-created content — completed stories, in-progress saves, generated images, generated videos, user profiles, and character photos — persists across container rebuilds, restarts, and code deployments. Data is never lost when updating the app.

**Why this priority**: Critical — losing family stories and generated artwork would be unacceptable. This is co-equal with getting the app running.

**Independent Test**: Create a story with images, deploy a code update, and verify the story and images are still accessible in the gallery after the deploy completes.

**Acceptance Scenarios**:

1. **Given** stories and images exist in the gallery, **When** the app container is rebuilt and restarted, **Then** all stories and images are still accessible.
2. **Given** an in-progress story is being played, **When** a deploy happens, **Then** the in-progress save is preserved and the user can resume after the app comes back up.
3. **Given** user profiles with character photos exist, **When** the container is replaced, **Then** all profiles and photos remain intact.
4. **Given** the app has been running for weeks accumulating data, **When** the developer checks storage usage, **Then** all data files are stored outside the container in a persistent location on the NUC's filesystem.

---

### Edge Cases

- What happens if the NUC's IP address changes? The user has a DHCP reservation at 192.168.4.152, so this is stable. The deploy script uses the hostname `warp-nuc` which can be updated if needed.
- What happens if API keys are not configured? The app starts but story generation fails gracefully with user-friendly error messages (existing app behavior). The setup process documents API key configuration.
- What happens if the deploy script is run while someone is actively using the app? The container restarts briefly (< 30 seconds downtime). In-progress stories are persisted to disk and survive the restart.
- What happens if the NUC runs out of disk space? The app continues to function for reading/browsing. New image generation fails with existing error handling. Monitoring disk usage is out of scope.
- What happens if the container build fails during a deploy? The existing running containers continue serving. The developer sees build errors in the deploy output.
- What happens if the app writes to new directories at runtime? The persistent storage configuration covers all directories the app writes to (data/ and static/images/ and static/videos/).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A setup script MUST configure the app on the NUC with a single command, handling container image building and service startup.
- **FR-002**: The app MUST run as two containers — one for the application server and one for the reverse proxy.
- **FR-003**: Containers MUST start automatically when the NUC boots, without manual intervention.
- **FR-004**: Containers MUST restart automatically if they crash or exit unexpectedly.
- **FR-005**: The app MUST be accessible from any device on the home LAN via `http://192.168.4.152/` on port 80.
- **FR-006**: The reverse proxy MUST forward port 80 traffic to the application container's internal port.
- **FR-007**: All persistent data (stories, images, videos, profiles, character photos, in-progress saves) MUST be stored outside the container filesystem so data survives container rebuilds.
- **FR-008**: A deploy script MUST allow the developer to update the running app from their laptop with a single command using SSH (user: jabelk, key-based auth).
- **FR-009**: The deploy script MUST pull the latest code, rebuild the app container, and restart services.
- **FR-010**: The deploy script MUST handle errors gracefully — a failed deploy MUST NOT take down the currently running app.
- **FR-011**: Application logs MUST be accessible via standard container logging tools.
- **FR-012**: API keys and environment configuration MUST be stored in a configuration file on the NUC, not in the repository.
- **FR-013**: The setup and deploy scripts MUST provide clear output indicating success or failure of each step.
- **FR-014**: All deployment configuration files MUST be included in the repository under a `deploy/` directory.
- **FR-015**: The container orchestration configuration MUST define both containers, their networking, and persistent storage in a single configuration file.

### Key Entities

- **App Container**: The application server running uvicorn, serving the web app on an internal port.
- **Proxy Container**: The reverse proxy forwarding external port 80 to the app container.
- **Persistent Volumes**: Named storage locations mapping container paths to NUC filesystem paths for stories, images, videos, profiles, and photos.
- **Environment File**: Configuration file on the NUC containing API keys and other secrets, excluded from the repository.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The app is accessible from a phone on the home LAN within 3 minutes of running the setup command on a fresh clone.
- **SC-002**: After a NUC reboot, the app is accessible within 60 seconds without manual intervention.
- **SC-003**: A code deploy from the developer's laptop takes less than 2 minutes from command to live.
- **SC-004**: All user data (stories, images, profiles) survives container rebuilds with zero data loss.
- **SC-005**: The entire deployment configuration is contained within the repository — no external dependencies beyond the NUC's base OS and container runtime (both already installed).
- **SC-006**: The developer can view application logs with a single command.

## Assumptions

- The NUC runs Ubuntu 24.04 with Docker and Docker Compose already installed and running.
- The developer has SSH key access configured from their laptop to the NUC (user: jabelk, no password required).
- The NUC has a stable IP address at 192.168.4.152 via DHCP reservation.
- The NUC has internet access for pulling container base images and for API calls during app usage.
- The NUC hostname is "warp-nuc".
- Port 80 is available on the NUC (no other web server running).
- The previous bare-metal deployment files (deploy/setup.sh, deploy/deploy.sh, deploy/choose-adventure.service) will be replaced by the new container-based approach.
- HTTPS is not required for initial deployment (LAN-only access).

## Out of Scope

- HTTPS/TLS certificate setup
- Container orchestration beyond Docker Compose (no Kubernetes, Swarm, etc.)
- CI/CD pipeline (deploy script is sufficient for a one-person project)
- Monitoring, alerting, or health check dashboards
- Backup automation for story data
- Multi-machine deployment or load balancing
- DNS configuration or custom domain names
- Container registry (images are built locally on the NUC)
