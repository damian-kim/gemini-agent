```markdown
# Plan: VPS Deployment - 2026-06-07

## 1. Goal
Deploy the Gemini Agent OS production container to an Oracle Cloud Infrastructure Ampere A1 Flex VPS, ensuring the FastAPI application and Gemini chat endpoint are functional. This plan focuses on achieving the "FastAPI app runs locally and on VPS" and "Gemini chat endpoint works" success criteria for the `gemini-agent-os` project.

## 2. Assumptions
*   The Oracle VPS is already provisioned, running a compatible Linux distribution (e.g., Ubuntu, Oracle Linux), and accessible via SSH.
*   Basic system administration tools (e.g., `git`, `curl`, `vim`/`nano`) are available on the VPS.
*   Docker and Docker Compose are installed and configured on the VPS.
*   The local development environment has a working FastAPI application for the Agent OS.
*   A Gemini API key is available and can be securely provided to the deployed application.
*   Basic network security (firewall rules) can be configured on the VPS to allow necessary inbound traffic.

## 3. Scope
This plan covers the initial deployment of the core Agent OS FastAPI application to the Oracle VPS.

**In-scope:**
*   Containerizing the FastAPI application using Docker.
*   Defining the application's services using Docker Compose.
*   Securely transferring the application code and configuration to the VPS.
*   Deploying and running the Docker Compose stack on the VPS.
*   Verifying the FastAPI application's health endpoint.
*   Verifying the Gemini chat endpoint's functionality on the VPS.

**Out-of-scope (for this initial plan):**
*   Setting up HTTPS/SSL certificates.
*   Configuring a custom domain name.
*   Implementing persistent storage beyond the application container (e.g., databases, external volumes).
*   Integrating external connectors (Gmail, Google Calendar, Notion, GitHub, etc.).
*   Advanced monitoring or logging solutions.
*   Automated deployment pipelines (CI/CD).
*   Public exposure of the application (initial deployment will focus on internal/private access).

## 4. Milestones

1.  **Local Containerization Complete:** FastAPI application successfully runs in Docker locally.
2.  **VPS Prepared:** Docker, Docker Compose, and necessary dependencies installed on the Oracle VPS.
3.  **Application Deployed:** Agent OS application successfully built and running via Docker Compose on the VPS.
4.  **Core Functionality Verified:** FastAPI health check and Gemini chat endpoint confirmed working on the VPS.

## 5. Step-by-step plan

### Block 0: Local Setup (Prerequisite: "Complete Block 0 local setup" from `task_20260607_001`)
1.  **Create `Dockerfile`:** Define the Dockerfile for the FastAPI application, specifying base image, dependencies, and application startup command.
2.  **Create `docker-compose.yml`:** Define the service for the FastAPI application, including port mappings, environment variables, and volume mounts (if any).
3.  **Local Docker Build & Run:** Build the Docker image locally and run the container using Docker Compose to verify it starts correctly and the health endpoint is accessible.
4.  **Local Gemini Test:** Test the Gemini chat endpoint locally within the Docker container to ensure API key and model configuration are correct.

### Block 1: VPS Preparation
1.  **SSH Access:** Ensure SSH access to the Oracle VPS is configured and working.
2.  **Install Docker & Docker Compose:** If not already present, install Docker Engine and Docker Compose on the VPS.
3.  **Firewall Configuration:** Configure the VPS firewall (e.g., `ufw` or Oracle Cloud's network security groups) to allow inbound traffic on the port the FastAPI app will expose (e.g., 8000).

### Block 2: Deployment
1.  **Code Transfer:** Securely transfer the `agent-os` project directory (including `Dockerfile`, `docker-compose.yml`, and application code) to the VPS using `scp` or `rsync`.
2.  **Environment Variables:** Set up environment variables for the Gemini API key on the VPS. This can be done via a `.env` file for Docker Compose or directly in the `docker-compose.yml` (less secure for sensitive keys). *Decision needed: Secure API key management.*
3.  **Docker Compose Up:** Navigate to the project directory on the VPS and run `docker compose build` followed by `docker compose up -d` to build the image and start the containers in detached mode.

### Block 3: Verification
1.  **Health Check:** Access the FastAPI health endpoint from your local machine (or via `curl` on the VPS) to confirm the application is running.
2.  **Gemini Endpoint Test:** Send a test request to the Gemini chat endpoint on the VPS to verify successful communication with the Gemini API.
3.  **Logs Review:** Check Docker container logs (`docker compose logs -f`) for any errors or warnings during startup and operation.

---
**Cut Order:** If time or resources are constrained, the first cut would be to ensure the FastAPI app runs on the VPS without the Gemini endpoint fully tested, relying on local testing for Gemini functionality. The absolute minimum is Block 0 (local containerization) and Block 2 (deployment) with a basic health check.

## 6. Risks
*   **Network Configuration:** Incorrect firewall rules on the VPS or Oracle Cloud security lists could prevent access to the deployed application.
*   **Dependency Issues:** Differences in OS or package versions between local and VPS environments could lead to unexpected errors.
*   **Gemini API Key Security:** Improper handling of the API key during transfer or storage on the VPS could expose credentials.
*   **Resource Constraints:** The Oracle Ampere A1 Flex VPS might have limited resources, potentially impacting application performance or stability.
*   **Docker/Docker Compose Version Mismatch:** Incompatibilities between local and VPS Docker versions could cause deployment issues.

## 7. Decisions Needed
*   **API Key Management:** How will the Gemini API key be securely stored and provided to the Docker container on the VPS? (e.g., `.env` file, Docker secrets, direct environment variable injection).
*   **Access Strategy:** For the MVP, should the application be accessible via public IP (with firewall restrictions) or only through a private VPN/Tailscale connection? (Refer to `memory/personal-os/open-threads.md`).
*   **Port Mapping:** Which external port on the VPS should be mapped to the internal FastAPI port (e.g., 8000)?

## 8. Next Action
Complete Block 0: Create the `Dockerfile` and `docker-compose.yml` for the FastAPI application and verify local Docker build and run.
```