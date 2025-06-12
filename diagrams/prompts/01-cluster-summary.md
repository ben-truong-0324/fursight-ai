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
* **Ingress Controller:** Traefik (installed by default with k3d). The Traefik dashboard is accessible and secured via HTTPS.
* **Internal Load Balancer:** MetalLB is installed and configured to provide `LoadBalancer` services with IPs from the internal Docker network.
* **TLS & Certificate Management:** `cert-manager` is installed. A `selfsigned-issuer` has been configured to provide automatic HTTPS for local services.

## III. Deployed Applications
1.  **`whoami` Service (for testing):**
    * Exposed via a standard `Ingress` object.
    * Secured with a self-signed certificate from `cert-manager`.
2.  **Traefik Dashboard:**
    * Exposed via a standard `Ingress` object in the `kube-system` namespace.
    * Secured with a self-signed certificate from `cert-manager`.
3.  **`frontend-nextjs` Application:**
    * A standard Next.js landing page created with `create-next-app`.
    * Containerized using an optimized multi-stage `Dockerfile`.
    * The image `frontend-nextjs:0.1.0` was built locally and loaded directly into the cluster using `k3d image import`. No external registry is being used.
    * Deployed via a custom Helm chart located in `infra/kubernetes/charts/frontend-nextjs`.
    * Exposed and secured with a standard `Ingress` at `https://app.fursight.local:9443`.

## IV. Established Conventions & File Structure
The project follows a clean Infrastructure-as-Code (IaC) structure.

├── apps/
│   └── frontend-nextjs/       # Next.js application code
│       ├── Dockerfile
│       └── .dockerignore
└── infra/
└── kubernetes/
├── charts/
│   └── frontend-nextjs/   # Helm chart for the Next.js app
└── manifests/
├── apps/
│   └── whoami/        # Manifests for the whoami test app
├── cert-manager/
│   └── self-signed-issuer.yaml
├── metallb/
│   └── config.yaml
└── traefik-dashboard-ingress.yaml

* Kubernetes manifests are organized by component/application.
* Helm is used for deploying our own applications.
* `cert-manager` handles TLS.
* All hostnames are managed in the local `/etc/hosts` file.