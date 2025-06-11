# Fursight Kubernetes + Docker Setup

## 🚀 Setup Instructions (Local Dev with Minikube)

### 📦 Requirements
- Docker Desktop
- Minikube
- kubectl


### ⚙️ 1. Start Minikube and deploy with script
```bash
minikube start -p fursight
minikube profile fursight 
minikube -p minikube docker-env
kubectl config use-context fursight
kubectl create namespace fursight
kubectl config set-context --current --namespace=fursight
```
### ⚙️ 1b. Deploy with script
```bash
#Windows
.\scripts\deploy_win.bat
# Mac
chmod +x ./scripts/deploy_mac.sh
./scripts/deploy_mac.sh
> This script builds images, deletes and reapplies all manifests, and shows you the service IPs

### 🌍 2. Access the App
- App: `http://fursight.local` or the LoadBalancer IP for `frontend`
- Frontend: `localhost:81`
- Backend: `localhost:80`
- Grafana: `localhost:3000`
- Prometheus: `localhost:9090`
- Kafdrap: `localhost:9000`


### 🧪 3. Check Status
```bash
kubectl get pods
kubectl get svc
kubectl get ingress
kubectl describe podht
```
