# Project Roadmap & History

## I. Completed: Path A - Strengthen the Platform
The initial platform has been strengthened with a complete monitoring solution.
* **DONE:** Installed and configured the `kube-prometheus-stack` Helm chart.
* **DONE:** Exposed the Grafana service via a secure Ingress.
* **DONE:** Logged into Grafana and confirmed access to default dashboards.

## II. Next Steps: Path B - Build the Application
Our current goal is to build and deploy a backend API and integrate it with the existing frontend.
1.  **Create FastAPI Backend:** Create a simple "Hello World" FastAPI application.
2.  **Containerize & Ship:** Write a `Dockerfile` for the Python app, build it, and import it into the `k3d` cluster.
3.  **Deploy with Helm:** Create a new Helm chart for the FastAPI backend.
4.  **Integrate:** Configure the `frontend-nextjs` application to make an API call from a `/demo` page to the FastAPI backend via its internal Kubernetes service name.