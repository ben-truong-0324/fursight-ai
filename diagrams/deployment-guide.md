# FurrSight AI: Implementation Steps (Manual Setup on macOS)

---

## Phase 0: Initial Setup & Prerequisites

1.  **On Local Machine (macOS):**
    - k3s is the right tradeoff for scope, but k3s wants Ubuntu VM. For MacOS, we use k3s in Docker aka k3d
      ```bash
      brew install git docker kubectl helm k3d

      Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

      choco install git kubernetes-cli kubernetes-helm k3d -y
      ```
    - Install and run **Docker Desktop**.

2.  **Project Setup:**
    - Clone empty Git repository: `git clone <repo-url>`
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
    - Exposes the Kubernetes API on your local machine at port 6443, Maps port 9080 on localhost to port 80 on the cluster's LB, same for 9443 to 443.
      ```bash
      k3d cluster create fursight --api-port 6443 -p "9080:80@loadbalancer" -p "9443:443@loadbalancer"
      ```

2.  **Verify Access:**
    - `k3d` automatically configures your `kubeconfig` file. Verify the connection with `kubectl`:
      ```bash
      kubectl get nodes
      # You should see one node named 'k3d-fursight-server-0' in a 'Ready' state.
      ```

2.  **For Dev:**
    - Create a local DNS on host:
      ```bash
      sudo nano /etc/hosts
      127.0.0.1 traefik.fursight.local # add this to last line
      127.0.0.1 whoami.fursight.local

      control + O, Enter, Control + X
      ```


## Phase B: Setup initial Traefik routing

1.  **Create yaml for traefik ingress for first routing: Traefik dashboard**
      ```bash
      cd infra/kubernetes/manifests
      touch traefik-dashboard-ingress.yaml

      apiVersion: traefik.containo.us/v1alpha1
      kind: IngressRoute
      metadata:
        name: traefik-dashboard
      spec:
        entryPoints:
          - web #http port from configured host port xxxx to cluster port 80
        routes:
          - match: Host(`traefik.fursight.local`)
            kind: Rule
            services:
              - name: api@internal
                kind: TraefikService
      ```
2.  **Verify Access: you now have http access (ingress route from local) to Traefik dashboard**
      traefik.fursight.local:9080


3.  **Create yaml for whoami ingress for second http routing: whoami**
      ```bash
      cd infra/kubernetes/manifests
      mkdir -p apps/whoami

      touch app.yaml ingress.yaml

      # app.yaml
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: whoami-deployment
      spec:
        replicas: 1
        selector:
          matchLabels:
            app: whoami
        template:
          metadata:
            labels:
              app: whoami
          spec:
            containers:
              - name: whoami-container
                image: "traefik/whoami" # A simple "whoami" web server from Traefik
                ports:
                  - containerPort: 80 # The application inside the container listens on port 80


      apiVersion: v1
      kind: Service
      metadata:
        name: whoami-service
      spec:
        selector:
          app: whoami # This connects the Service to the Deployment above
        ports:
          - name: web # We can name the port
            protocol: TCP
            port: 80 # The Service will be available on port 80 inside the cluster
            targetPort: 80 # The Service will forward traffic to port 80 on the pods

      # ingress.yaml
      apiVersion: traefik.containo.us/v1alpha1
      kind: IngressRoute
      metadata:
        name: whoami-ingress
      spec:
        entryPoints:
          - web
        routes:
          - match: Host(`whoami.fursight.local`)
            kind: Rule
            services:
              - name: whoami-service # Tells Traefik to send traffic to our new service
                port: 80

        kubectl apply -f .
      ```
4.  **Verify Access: you now have http access (ingress route from local) to whoami**
      whoami.fursight.local:9080

5.  This has been setting up deploy, ingress with traefik the "manual" way. 
---

## Phase C: MetalLB and CertManager

**Goal:** MetalLB assigns external IP to ingress and LB services in cluster (Cloud providers will have their own MetalLB, so we're simulating.) MetalLB is L4 and assigns LB IPs. Traefik is ingress ctl which handle rules and routes within cluster - it is L7 and assigns service IPs needing ingress.


1.  **Add Helm Repositories:**
    `helm repo add bitnami https://charts.bitnami.com/bitnami`
    `helm repo update`

2.  **Create cluster level metallb folder:**
    - From manifests/apps, cd.. 
        ```bash
        mkdir metallb
        touch metallb/config.yaml
        
        helm repo add metallb https://metallb.github.io/metallb
        helm repo update
        helm install metallb metallb/metallb --create-namespace --namespace metallb-system

        docker network inspect k3d-fursight-ai | grep Subnet

        # metallb-config.yaml
        apiVersion: metallb.io/v1beta1
        kind: IPAddressPool
        metadata:
          name: default-pool
          namespace: metallb-system
        spec:
          addresses:
            - 172.22.0.200-172.22.0.250 #  docker network inspect k3d-fursight-ai | grep Subnet    "Subnet": "172.22.0.0/16",
        ---
        apiVersion: metallb.io/v1beta1
        kind: L2Advertisement
        metadata:
          name: default
          namespace: metallb-system


        kubectl apply -f .

        kubectl get svc loadbalancer  
        kubectl get svc -n kube-system traefik
        
        ```


## Phase D: cert-manager setup (in lieu for Lets Encrypt)

**Goal:** Let's Encrypt's servers must publicly verify that you own the domain via public DNS provider (like GoDaddy or Cloudflare.) So we simulate https by becoming our own CA with self-signed certificates. 



1.  **Add Helm Repositories:**
    `helm repo add jetstack https://charts.jetstack.io
      helm repo update
      helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --version v1.14.5 --set installCRDs=true`

2.  **Create cluster level cert-manager folder:**
    - At infra/kubernetes/manifests/
        ```bash
        mkdir cert-manager
        cd cert-manager
        touch self-signed-issuer.yaml

        # infra/kubernetes/manifests/cert-manager/self-signed-issuer.yaml
        apiVersion: cert-manager.io/v1
        kind: ClusterIssuer
        metadata:
          name: selfsigned-issuer
        spec:
          selfSigned: {}

        kubectl apply -f .

3.  **Add TLS to whoami**
    - Update tls under spec for whoami ingress
    # infra/kubernetes/manifests/apps/whoami/ingress.yaml
    # whoami-ingress.yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: whoami-ingress
      annotations:
        cert-manager.io/cluster-issuer: "selfsigned-issuer" # Tell cert-manager to use our issuer
        traefik.ingress.kubernetes.io/router.entrypoints: websecure # Tell Traefik to use the secure entrypoint
    spec:
      ingressClassName: traefik # Important: Tell Kubernetes this is for Traefik
      rules:
      - host: "whoami.fursight.local"
        http:
          paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: whoami-service
                port:
                  number: 80
      tls: # This section requests a certificate
      - hosts:
        - "whoami.fursight.local"
        secretName: whoami-tls-secret # cert-manager will create a secret with this name


      kubectl delete ingressroute whoami-ingress      
      # now change to ingress
      # https://whoami.fursight.local:9443 #switched to https port
      kubectl get certificate 

      A Certificate is not a standard, built-in Kubernetes object like a Pod or a Service. It's a special resource type, called a Custom Resource Definition (CRD), that was added to your cluster's API when we installed cert-manager


3.  **Add TLS to Traefik dashboard**
    - kubectl delete ingressroute traefik-dashboard

    # infra/kubernetes/manifests/traefik-dashboard-ingress.yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: traefik-dashboard-ingress
      namespace: kube-system # Create this Ingress in the kube-system namespace
      annotations:
        cert-manager.io/cluster-issuer: "selfsigned-issuer" # Use our self-signed issuer
    spec:
      ingressClassName: traefik
      rules:
      - host: "traefik.fursight.local"
        http:
          paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: traefik # The name of the Traefik service
                port:
                  number: 9000 # The port for the dashboard API
      tls:
      - hosts:
        - "traefik.fursight.local"
        secretName: traefik-dashboard-tls-secret # cert-manager will create this


kubectl get service traefik -n kube-system
# eed to export port 9000 to the dashboard now with https
# when http, we used IngressRoute which had built in api@internal to dashboard

kubectl patch service traefik -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/ports/-", "value": {"name": "traefik", "port": 9000, "targetPort": 9000, "protocol": "TCP"}}]'

https://traefik.fursight.local:9443/dashboard/ 

#IngressRoute is created by Traefik, for Traefik. It’s not built into Kubernetes. It's a Custom Resource Definition (CRD) that Traefik adds (have Traefik middleware, traffic splitting, etc. by default)



### Step 3: Create frontend with Nextjs

cd apps/
npx create-next-app@latest
cd frontend-nextjs
npm run dev

## create docker img

# Dockerfile
# Dockerfile

# ---- Stage 1: Build the application ----
# Use the official Node.js 20 image as a base for building.
# 'alpine' is a lightweight version of Linux.
FROM node:20-alpine AS builder

# Set the working directory inside the container.
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker layer caching.
# This step only re-runs if these files change.
COPY package*.json ./
RUN npm install

# Copy the rest of the application source code.
COPY . .

# Build the Next.js application for production.
RUN npm run build

# ---- Stage 2: Create the final production image ----
# Use a minimal Node.js image for the final container.
FROM node:20-alpine AS runner

WORKDIR /app

# Create a non-root user for security best practices.
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy the built application from the 'builder' stage.
# This includes the .next folder (standalone output), public folder, and package.json.
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json .

# Next.js in standalone mode doesn't need all node_modules, only a few.
# By running a minimal install, we keep the image size down.
RUN npm install --omit=dev --production

# Change ownership of the files to our non-root user.
RUN chown -R nextjs:nodejs .

# Switch to the non-root user.
USER nextjs

# Expose the port the app will run on.
EXPOSE 3000

# The command to start the Next.js server in production mode.
CMD ["npm", "start"]

# .dockerignore

.DS_Store
.env.local
.git
.next
.vercel
node_modules
npm-debug.log*
README.md

docker build -t frontend-nextjs:0.1.0 .

k3d image import frontend-nextjs:0.1.0 -c fursight-ai
# "packaged" and "shipped" application is now available inside the cluster,

cd infra/kubernetes/charts

### Step 3.1: Create the Custom Helm Chart
helm create frontend-nextjs

# at charts/frontend-nextjs/

# Remove files we are not using
rm templates/tests/test-connection.yaml
rm templates/hpa.yaml
rm templates/serviceaccount.yaml
rm templates/NOTES.txt

# Overwrite config in values.yaml to
# values.yaml
# -- Replica count for the deployment
replicaCount: 1

image:
  # -- The repository (name) of the image we loaded into k3d
  repository: frontend-nextjs
  # -- The tag of the image we built (e.g., 0.1.0)
  tag: "0.1.0"
  # -- Since the image is already in the cluster, we don't need to pull it from a remote registry.
  # IfNotPresent means it will only pull if the image is not already on the node.
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  # -- The port your Next.js application listens on inside the container
  port: 3000

ingress:
  enabled: true
  # -- We must specify our traefik ingress class
  className: "traefik"
  annotations:
    # -- Add cert-manager annotation to automatically get a certificate
    cert-manager.io/cluster-issuer: "selfsigned-issuer"
  hosts:
    - host: "app.fursight.local" # <-- Your app's desired hostname
      paths:
        - path: /
          pathType: Prefix
  tls:
   - secretName: frontend-tls-secret # <-- cert-manager will create this secret
     hosts:
       - "app.fursight.local" # <-- The hostname to secure

serviceAccount:
  create: false
autoscaling:
  enabled: false

# this will be frontend so wanna give it a domain, plus use ingress as TLS
sudo nano /etc/hosts
127.0.0.1 app.fursight.local

# in infra/kubernetes/charts/
helm install frontend-release ./frontend-nextjs --namespace default


https://app.fursight.local:9443



#### Add monitoring

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring
kubectl get pods -n monitoring -w
# to customize, do helm upgrades

cd infra/kubernetes/manifests
mkdir monitoring
cd monitoring
touch prometheus-values.yaml
'''
# infra/kubernetes/manifests/monitoring/prometheus-values.yaml
grafana:
  ingress:
    enabled: true
    ingressClassName: traefik
    annotations:
      cert-manager.io/cluster-issuer: selfsigned-issuer
    hosts:
      - grafana.fursight.local
    path: /
    pathType: Prefix
    tls:
      - secretName: grafana-tls
        hosts:
          - grafana.fursight.local
'''

helm upgrade prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  -f infra/kubernetes/manifests/monitoring/prometheus-values.yaml

helm chart default:
Username: admin
Password: prom-operator





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
