# Project Roadmap & History

## I. Completed: Path A - Strengthen the Platform
* **DONE:** Installed and configured the `kube-prometheus-stack` Helm chart.
* **DONE:** Exposed the Grafana service via a secure Ingress.

## II. Completed: Path B - Build the Application
* **DONE:** Created a "Hello World" FastAPI application using Poetry.
* **DONE:** Containerized the application using a multi-stage `Dockerfile`.
* **DONE:** Deployed the application into the cluster using a dedicated Helm chart.
* **DONE:** Integrated the `frontend-nextjs` application to fetch data from the backend.

## III. Next Steps: Path C - Deploy AI/ML Inference Server on Windows/NVIDIA
Our new goal is to build a new cluster on a Windows host with an NVIDIA GPU. We will deploy a vLLM server that leverages this hardware.
1.  **Prepare Windows Host & Create GPU-Enabled Cluster:** Install all necessary prerequisites on the Windows machine (NVIDIA Drivers, WSL2, CUDA for WSL) and create a new `k3d` cluster with GPU pass-through enabled.
2.  **Install NVIDIA GPU Operator:** Deploy the official NVIDIA GPU Operator via Helm. This will automatically configure the cluster nodes with the required drivers and container runtimes to manage the GPU.
3.  **Deploy vLLM Server (GPU):** Create Kubernetes manifests (`Deployment` and `Service`) to run a vLLM server pod that requests a GPU resource.
4.  **Test the Service:** Port-forward to the pod and use `curl` to interact with the OpenAI-compatible `/v1/completions` endpoint to verify GPU-accelerated inference.