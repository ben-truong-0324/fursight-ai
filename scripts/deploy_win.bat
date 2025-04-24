@echo off
echo 🚀 Starting Fursight Deployment with Local Docker Builds + Minikube Tunnel...

:: Step 1: Configure Minikube Docker daemon
echo 🔄 Setting Docker to use Minikube's internal Docker engine...
@REM FOR /F "delims=" %%i IN ('minikube docker-env --shell cmd') DO %%i
@REM FOR /f "tokens=*" %%i IN ('minikube docker-env --shell=cmd') DO @%%i
FOR /F "delims=" %%i IN ('minikube -p fursight docker-env --shell cmd') DO @%%i

:: Step 2: Rebuild Docker images locally inside Minikube
echo 🐳 Building local Docker images...
docker build -t fursight/frontend ./frontend
docker build -t fursight/backend ./backend
docker build -t fursight/ollama ./ollama
docker build -t fursight/db ./db
docker build -t fursight/kafka ./kafka

:: Step 3: Start Minikube tunnel in a separate terminal
echo 🌐 Starting Minikube tunnel (required for LoadBalancer IPs)...
start "Minikube Tunnel" cmd /k "cd /d %CD% && minikube tunnel"

:: Step 4: Optional - Mount shared data folder
echo 📁 Mounting ./data into Minikube...
start "Minikube Mount" cmd /k "cd /d %CD% && minikube mount ./data:/mnt/data"

:: Step 5: Re-apply Kubernetes manifests
echo 📦 Redeploying Kubernetes components...

kubectl delete -f k8s/ --ignore-not-found
kubectl apply -f k8s/

:: Step 6: Wait for critical services to be ready
echo ⏳ Waiting for Deployments to become available...
kubectl wait --for=condition=available deployment/frontend --timeout=120s
kubectl wait --for=condition=available deployment/backend --timeout=120s
kubectl wait --for=condition=available deployment/ollama --timeout=120s

:: Step 7: Output service endpoints
echo 🌍 Getting service IPs and Ingress rules...
kubectl get svc -o wide
kubectl get pods
kubectl get ingress

echo ✅ Fursight fully deployed using Minikube + local builds!
echo 🔗 Access via localhost:81 or EXTERNAL-IP from above
echo Flask Frontend Logs:

kubectl logs deployment/frontend -f