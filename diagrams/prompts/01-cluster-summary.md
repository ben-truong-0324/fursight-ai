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
    * Configuration is managed via `infra/kubernetes/manifests/monitoring/prometheus-values.yaml`.

## IV. Deployed Applications
1.  **`whoami` Service (for testing):**
    * Exposed via a standard `Ingress` object.
2.  **Traefik Dashboard:**
    * Exposed via a standard `Ingress` object.
3.  **`frontend-nextjs` Application:**
    * Deployed via a custom Helm chart.
    * Exposed and secured with a standard `Ingress` at `https://app.fursight.local:9443`.

## V. Established Conventions & File Structure
The project follows a clean Infrastructure-as-Code (IaC) structure.

├── apps/
│   └── frontend-nextjs/
│       ├── Dockerfile
│       └── .dockerignore
└── infra/
    └── kubernetes/
        ├── charts/
        │   └── frontend-nextjs/
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

* Helm is used for deploying our own applications and configuring third-party applications.
* `cert-manager` handles TLS.
* All hostnames are managed in the local `/etc/hosts` file.