FurrSight AI: Single-Node Development Deployment Guide
1. Objective
This guide details the process of deploying the complete FurrSight AI application stack onto a single development server. The primary goal is to create a robust, self-contained, and secure environment that closely mirrors a full-scale cloud deployment.

We will use a lightweight, single-node Kubernetes distribution (k3s) as our cluster, provision it using Ansible, and manage all application deployments using Helm. Authentication will be handled by a central Identity Provider (IdP).

2. Prerequisites
Development Server: A single server (e.g., a VPS or bare-metal machine) with a modern Linux distribution (e.g., Ubuntu 22.04). It should have sufficient resources (e.g., 4+ CPU cores, 16GB+ RAM) and ideally a GPU accessible to Docker for the ML-heavy phases.

Local Machine: Your personal computer where you will run ansible and kubectl commands. Ansible must be installed.

Domain/DNS: A domain name with subdomains pointing to your server's IP (e.g., fursight.dev.mydomain.com, auth.dev.mydomain.com).

Git Repository: All application code and Kubernetes configurations (including Helm charts) should be hosted in a Git repository.

Container Registry: A place to store your built Docker images (e.g., Docker Hub, GitHub Container Registry, etc.).

3. Deployment Strategy
The deployment is executed in three main phases: provisioning the cluster, deploying third-party dependencies (including the IdP), and finally deploying our custom FurrSight AI microservices.

Phase A: Cluster Provisioning with Ansible

Goal: Automate the transformation of a bare Linux server into a fully functional, single-node Kubernetes cluster.

An Ansible playbook will be created to execute the following tasks on the remote development server:

Node Preparation:

Install necessary dependencies: docker, curl, etc.

Configure system settings required for Kubernetes, like firewall rules.

Install k3s (Lightweight Kubernetes):

Download and install k3s, which includes a built-in Ingress controller (Traefik).

Configure kubectl Access:

Securely copy the kubeconfig file from the server to your local machine.

Verify Cluster:

Run kubectl get nodes from your local machine to confirm the cluster is ready.

Phase B: Deploying Backend Dependencies with Helm

Goal: Deploy the stateful services and the IdP using pre-built, community-maintained Helm charts.

Identity Provider (Keycloak):

Chart: bitnami/keycloak

Configuration: Deploy Keycloak and create an Ingress to expose it on a dedicated subdomain (e.g., auth.dev.mydomain.com). After deployment, manually configure a "realm," a client for the FurrSight application, and user accounts for the research team.

PostgreSQL (Metadata Store):

Chart: bitnami/postgresql

Configuration: Configure with a PersistentVolume using the local-path provisioner to ensure data persistence.

Redis (Cache & Task Queue):

Chart: bitnami/redis

Configuration: A simple deployment is sufficient for development.

MinIO (S3-Compatible Object Storage):

Chart: bitnami/minio

Configuration: Configure with a PersistentVolume for persistent object storage.

Phase C: Deploying FurrSight AI Services with Helm

Goal: Package our custom microservices into Helm charts, configure them for OIDC authentication, and deploy them into the cluster.

Create Custom Helm Charts: Create a dedicated Helm chart for each service (nextjs-frontend, fastapi-backend, vllm-server, celery-workers).

Build & Push Docker Images (CI Step): Have a CI process to build and push versioned Docker images to your container registry.

Deploy the Application Stack (Manual Helm):

Secrets First: Create Kubernetes Secrets to hold the OIDC client ID and client secret obtained from Keycloak.

Deployment Order & Configuration:

vllm-server: Deploy first. Configure to mount the host's GPU device. This service runs on the internal network and does not need direct authentication.

fastapi-backend: Configure its values.yaml to:

Connect to PostgreSQL, Redis, and vLLM via their internal cluster DNS names.

Load the OIDC client credentials from the Kubernetes Secret.

Include environment variables for the OIDC issuer URL (e.g., https://auth.dev.mydomain.com/realms/fursight). Your FastAPI code will use this to validate JWTs from the frontend.

celery-workers: Configure similarly to the FastAPI backend, as it needs to connect to the same resources.

nextjs-frontend: Configure its Helm chart to:

Load OIDC configuration (issuer URL, client ID) to handle the OIDC login flow in the browser.

Create an Ingress resource to route traffic from fursight.dev.mydomain.com.

4. Verification and Usage
Once deployed, a researcher first navigates to fursight.dev.mydomain.com. They will be redirected to the Keycloak login page. After successful authentication, they are redirected back to the FurrSight application, where they can now interact with the UI to execute workflows.

5. Next Steps: Towards GitOps
This guide uses manual helm install commands. The next evolution is to adopt a GitOps workflow using a tool like Argo CD to automate deployments directly from your Git repository.
