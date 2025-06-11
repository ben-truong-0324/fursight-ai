#!/bin/bash

echo "🚀 Starting Fursight Deployment with Local Docker Builds + Minikube Tunnel..."

# Step 1: Configure Minikube Docker daemon
echo "🔄 Setting Docker to use Minikube's internal Docker engine..."
eval $(minikube -p fursight docker-env)

# Step 2: Rebuild Docker images locally inside Minikube
echo "🐳 Building local Docker images..."
docker build -t fursight/frontend ./frontend
docker build -t fursight/backend ./backend
docker build -t fursight/ollama ./ollama
docker build -t fursight/db ./db
docker build -t fursight/kafka ./kafka

# Step 3: Start Minikube tunnel in a new Terminal window
echo "🌐 Starting Minikube tunnel (required for LoadBalancer IPs)..."
osascript <<EOF
tell application "Terminal"
    do script "minikube tunnel"
end tell
EOF

# Step 4: Optional - Mount shared data folder
echo "📁 Mounting ./data into Minikube..."
osascript <<EOF
tell application "Terminal"
    do script "minikube mount $(pwd)/data:/mnt/data"
end tell
EOF

# Step 5: Re-apply Kubernetes manifests
echo "📦 Redeploying Kubernetes components..."
kubectl delete -f k8s/ --ignore-not-found
kubectl apply -f k8s/

# Step 6: Wait for critical services to be ready
echo "⏳ Waiting for Deployments to become available..."
kubectl wait --for=condition=available deployment/frontend --timeout=120s
kubectl wait --for=condition=available deployment/backend --timeout=120s
kubectl wait --for=condition=available deployment/ollama --timeout=120s

# Step 7: Output service endpoints
echo "🌍 Getting service IPs and Ingress rules..."
kubectl get svc -o wide
kubectl get pods
kubectl get ingress

echo "✅ Fursight fully deployed using Minikube + local builds!"
echo "🔗 Access via localhost:81 or EXTERNAL-IP from above"
echo "Flask Frontend Logs:"
kubectl logs deployment/frontend -f
