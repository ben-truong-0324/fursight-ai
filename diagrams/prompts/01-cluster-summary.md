# Project Summary & Current State

## I. High-Level Goal
The user is building a "best-in-class" local development environment on macOS. The architecture should mirror modern production practices, emphasizing containerization, Kubernetes, automation, and observability.

## II. Core Infrastructure
* **Host OS:** macOS
* **Kubernetes:** K3s running in Docker via `k3d`.
    * **Cluster Name:** `fursight-ai`
    * **Port Mappings (Host -> Cluster):**
        * `9080` -> `80` (HTTP)
        * `9443` -> `443` (HTTPS)
* **Ingress Controller:** Traefik (installed by default with k3d).
* **Internal Load Balancer:** MetalLB is installed and configured.
* **TLS & Certificate Management:** `cert-manager` is installed with a `selfsigned-issuer`.

## III. Platform Components
* **Observability:**
    * The `kube-prometheus-stack` Helm chart is installed in the `monitoring` namespace.
    * This provides cluster-wide metrics collection with Prometheus and visualization with Grafana.
    * Grafana is exposed via a standard `Ingress` at `https://grafana.fursight.local:9443`.

## IV. Deployed Applications
1.  **`whoami` Service (for testing):**
    * Exposed via a standard `Ingress` object.
2.  **Traefik Dashboard:**
    * Exposed via a standard `Ingress` object.
3.  **`frontend-nextjs` Application (v0.2.0):**
    * Deployed via a custom Helm chart.
    * Exposed and secured at `https://app.fursight.local:9443`.
    * Includes a `/demo` page that successfully fetches data from the `backend-fastapi` service.
4.  **`backend-fastapi` Application (v0.1.0):**
    * A Python FastAPI service created with Poetry.
    * Deployed via a custom Helm chart.
    * Exposed internally within the cluster via a `ClusterIP` service on port 8000.
5.  **`vllm-server` (Multi-Model):**
    * Deployed via a dynamic, reusable Helm chart.
    * Serves multiple language models concurrently (`opt-125m`, `gpt2`).
    * Exposed and secured via a Traefik `IngressRoute` at `https://vllm.fursight.local:9443`.
    * Uses path-based routing (`/models/<model-name>`) and `Middleware` to route to the correct model service.

## V. Established Conventions & File Structure
The project follows a clean Infrastructure-as-Code (IaC) structure.

├── apps/
│   ├── backend-fastapi/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── pyproject.toml
│   └── frontend-nextjs/
│       ├── Dockerfile
│       └── src/ # Using App Router
└── infra/
    └── kubernetes/
        ├── charts/
        │   ├── backend-fastapi/
        │   ├── frontend-nextjs/
        │   └── vllm-server/
        │       ├── Chart.yaml
        │       ├── templates/
        │       │   ├── deployment.yaml
        │       │   ├── ingressroute.yaml
        │       │   ├── middleware.yaml
        │       │   └── service.yaml
        │       └── values.yaml
        └── manifests/
            ├── apps/
            │   └── whoami/
            ├── cert-manager/
            │   └── self-signed-issuer.yaml
            ├── metallb/
            │   └── config.yaml
            ├── monitoring/
            │   └── prometheus-values.yaml
            └── traefik-dashboard-ingress.yaml