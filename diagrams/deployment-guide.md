# FurrSight AI: Implementation Steps (Manual Setup on macOS)

This guide details the simplest, most direct method to deploy the FurrSight stack on your local macOS machine. It removes the Ansible automation layer in favor of clear, manual commands for setting up the local cluster.

---

## Phase 0: Initial Setup & Prerequisites

**Goal:** Prepare your local machine with the necessary tools and project structure.

1.  **On Your Local Machine (macOS):**
    - Install **Homebrew** if you don't have it (this is the standard package manager for macOS).
    - Install necessary command-line tools using Homebrew:
      ```bash
      brew install git docker kubectl helm k3d
      ```
    - Install and run **Docker Desktop**.

2.  **Project Setup:**
    - Clone your empty Git repository: `git clone <your-repo-url>`
    - Create the initial project structure within the repository:
      ```
      fursight-ai/
      ├── applications/
      ├── infrastructure/
      │   └── kubernetes/
      │       └── charts/
      └── README.md
      ```

3.  **Domain Name via Tailscale:**
    - We will your domain `usr.tail.net`. All services will be exposed as subdomains (e.g., `fursight.usr.tail.net`, `auth.usr.tail.net`) if possible.

---

## Phase A: Cluster Setup (Manual)

**Goal:** Create a single-node k3s Kubernetes cluster running locally in Docker.

1.  **Create the Cluster:**
    - Run the following `k3d` command in your terminal. This creates a cluster named `fursight` and maps the Ingress ports from the cluster to your local machine, which is essential for Tailscale access.
      ```bash
      k3d cluster create fursight -p "89:80@loadbalancer" -p "449:443@loadbalancer"
      ```

2.  **Verify Access:**
    - `k3d` automatically configures your `kubeconfig` file. Verify the connection with `kubectl`:
      ```bash
      kubectl get nodes
      # You should see one node named 'k3d-fursight-server-0' in a 'Ready' state.
      ```

---

## Phase B & C: Deploying Dependencies & Applications

**Goal:** Use Helm to deploy all services into the cluster.

These steps are run directly from your Mac's terminal.

1.  **Add Helm Repositories:**
    `helm repo add bitnami https://charts.bitnami.com/bitnami`
    `helm repo update`

2.  **Install Dependencies:**
    - For each dependency, run `helm install`. 
        ```bash
        helm install keycloak bitnami/keycloak --set auth.adminPassword=placeholder-password
        helm install postgresql bitnami/postgresql --set auth.postgresPassword=your-strong-password
        helm install redis bitnami/redis --set auth.password=your-strong-password
        helm install minio bitnami/minio --set auth.rootPassword=your-strong-password #needs 8 char min len
        cd infra/kubernetes/manifests
        kubectl apply -f strip-prefix-middleware.yaml
        kubectl apply -f keycloak-ingress.yaml

        ```

**Goal:** Package, build, and deploy a custom service (`fastapi-backend`) using a local Docker image. You will repeat this pattern for all your other custom services.

### Step 3.1: Create the Custom Helm Chart
Create the boilerplate file structure for your application's "package."

1.  Navigate to your FastAPI application's source code directory:
    `cd apps/fastapi-backend/`
2.  Run the Helm command to create a new chart named `backend-chart`:
    `helm create backend-chart`
3.  Poetry init 
    poetry add fastapi "uvicorn[standard]" python-multipart sqlalchemy psycopg2-binary alembic celery redis "python-jose[cryptography]" "passlib[bcrypt]" pydantic-settings httpx

### Step 3.2: Containerize the Application & Import Local Image
Build a Docker image locally and load it directly into your k3d cluster, skipping a cloud registry.

1.  **Create a `Dockerfile`** in `apps/fastapi-backend/`:
    ```dockerfile
    # apps/fastapi-backend/Dockerfile
    FROM python:3.11-slim
    WORKDIR /app
    RUN pip install poetry
    COPY poetry.lock pyproject.toml ./
    RUN poetry install --no-dev --no-root
    COPY . .
    EXPOSE 8000
    CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
    ```
2.  **Build the Docker Image Locally.** From the `apps/fastapi-backend/` directory, run:
    ```bash
    docker build -t fursight-fastapi:0.1.0 .
    ```
3.  **Import the Local Image into your k3d Cluster.** This is the crucial step for a local-only workflow.
    ```bash
    k3d image import fursight-fastapi:0.1.0 --cluster fursight
    ```

### Step 3.3: Create Kubernetes Secrets
Securely store the OIDC client credentials you get from the Keycloak UI.

1.  **Create the file** `infra/kubernetes/manifests/fursight-secrets.yaml`:
    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: fursight-oidc-secret
    type: Opaque
    stringData:
      OIDC_CLIENT_ID: "fursight-client"
      OIDC_CLIENT_SECRET: "your-long-and-secure-client-secret-from-keycloak"
    ```
2.  **Apply it to the cluster:**
    `kubectl apply -f infra/kubernetes/manifests/fursight-secrets.yaml`

### Step 3.4: Configure the Helm Chart
Tell your Helm chart what image to use and what environment variables to set.

1.  **Edit `apps/fastapi-backend/backend-chart/values.yaml`**. This configures the image, environment variables, and Ingress routing.
    ```yaml
    # values.yaml for the FastAPI backend
    replicaCount: 1

    image:
      repository: fursight-fastapi # NOTE: No registry prefix needed
      pullPolicy: IfNotPresent   # Tells K8s to use the local image if the tag matches
      tag: "0.1.0"

    service:
      type: ClusterIP
      port: 8000

    ingress:
      enabled: true
      className: ""
      annotations:
        kubernetes.io/ingress.class: traefik
      hosts:
        - host: api.ben.tail.net
          paths:
            - path: /
              pathType: ImplementationSpecific
    
    env:
      - name: DATABASE_URL
        value: "postgresql://postgres:your-strong-password@postgresql.default.svc.cluster.local:5432/postgres"
      - name: REDIS_URL
        value: "redis://:your-strong-password@redis-master.default.svc.cluster.local:6379"
      - name: OIDC_ISSUER_URL
        value: "[https://auth.ben.tail.net/realms/fursight](https://auth.ben.tail.net/realms/fursight)"
      - name: OIDC_CLIENT_ID
        valueFrom:
          secretKeyRef:
            name: fursight-oidc-secret
            key: OIDC_CLIENT_ID
      - name: OIDC_CLIENT_SECRET
        valueFrom:
          secretKeyRef:
            name: fursight-oidc-secret
            key: OIDC_CLIENT_SECRET
    ```
2.  **Edit `apps/fastapi-backend/backend-chart/templates/deployment.yaml`**. Find the `env:` section under `containers:` and replace the placeholder block with this snippet to load your environment variables correctly:
    ```yaml
    # ... inside the container spec ...
              ports:
                - name: http
                  containerPort: {{ .Values.service.port }}
                  protocol: TCP
              env:
                {{- toYaml .Values.env | nindent 16 }}
              livenessProbe:
    # ... rest of the file ...
    ```

### Step 3.5: Install the Helm Chart
Deploy the application to your cluster.

1.  From your project's root directory (`fursight-ai/`), run the `helm install` command:
    ```bash
    helm install fastapi-backend ./apps/fastapi-backend/backend-chart/
    ```

After a minute, run `kubectl get pods`. You should see a pod for `fastapi-backend` in the `Running` state. You can now access your API at `http://api.ben.tail.net`.
