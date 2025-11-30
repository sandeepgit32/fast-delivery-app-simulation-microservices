#!/bin/bash

# Food Delivery Simulation App - Kubernetes Deployment Script
# This script deploys the entire application to Minikube in one shot

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="fast-delivery-dev"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Food Delivery App - Kubernetes Deployment${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_step() {
    echo -e "\n${BLUE}==>${NC} $1"
}

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    print_error "Minikube is not installed. Please install it first."
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it first."
    exit 1
fi

# Step 1: Start Minikube if not running
print_step "Step 1: Checking Minikube status..."
if minikube status | grep -q "Running"; then
    print_status "Minikube is already running"
else
    print_warning "Starting Minikube..."
    minikube start --cpus=4 --memory=8192
    print_status "Minikube started"
fi

# Step 2: Build Docker images
print_step "Step 2: Building Docker images..."
cd "$PROJECT_ROOT"

echo "Building api-gateway..."
docker build -t api-gateway:latest ./api-gateway

echo "Building order-service..."
docker build -t order-service:latest ./order-service

echo "Building delivery-service..."
docker build -t delivery-service:latest ./delivery-service

echo "Building stock-service..."
docker build -t stock-service:latest ./stock-service

echo "Building metrics-service..."
docker build -t metrics-service:latest ./metrics-service

echo "Building order-auto-generation-service..."
docker build -t order-auto-generation-service:latest ./order-auto-generation-service

echo "Building tasks (celery worker)..."
docker build -t tasks:latest ./tasks

echo "Building frontend-service..."
docker build -t frontend-service:latest ./frontend-service

print_status "All Docker images built successfully"

# Step 3: Load images into Minikube
print_step "Step 3: Loading images into Minikube..."

echo "Loading api-gateway..."
minikube image load api-gateway:latest

echo "Loading order-service..."
minikube image load order-service:latest

echo "Loading delivery-service..."
minikube image load delivery-service:latest

echo "Loading stock-service..."
minikube image load stock-service:latest

echo "Loading metrics-service..."
minikube image load metrics-service:latest

echo "Loading order-auto-generation-service..."
minikube image load order-auto-generation-service:latest

echo "Loading tasks..."
minikube image load tasks:latest

echo "Loading frontend-service..."
minikube image load frontend-service:latest

print_status "All images loaded into Minikube"

# Step 4: Deploy to Kubernetes
print_step "Step 4: Deploying to Kubernetes..."
cd "$SCRIPT_DIR"
kubectl apply -k .
print_status "Kubernetes manifests applied"

# Step 5: Wait for databases to be ready
print_step "Step 5: Waiting for databases to be ready..."

echo "Waiting for MySQL..."
kubectl wait --for=condition=ready pod -l app=mysql -n $NAMESPACE --timeout=180s

echo "Waiting for Redis..."
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=60s

echo "Waiting for InfluxDB..."
kubectl wait --for=condition=ready pod -l app=influxdb -n $NAMESPACE --timeout=60s

print_status "All databases are ready"

# Step 6: Wait for application services
print_step "Step 6: Waiting for application services..."

echo "Waiting for order-service..."
kubectl wait --for=condition=ready pod -l app=order-service -n $NAMESPACE --timeout=120s

echo "Waiting for delivery-service..."
kubectl wait --for=condition=ready pod -l app=delivery-service -n $NAMESPACE --timeout=120s

echo "Waiting for stock-service..."
kubectl wait --for=condition=ready pod -l app=stock-service -n $NAMESPACE --timeout=120s

echo "Waiting for api-gateway..."
kubectl wait --for=condition=ready pod -l app=api-gateway -n $NAMESPACE --timeout=120s

echo "Waiting for frontend-service..."
kubectl wait --for=condition=ready pod -l app=frontend-service -n $NAMESPACE --timeout=120s

print_status "All application services are ready"

# Step 7: Display status
print_step "Step 7: Deployment Status"

echo -e "\n${BLUE}Pods:${NC}"
kubectl get pods -n $NAMESPACE

echo -e "\n${BLUE}Services:${NC}"
kubectl get svc -n $NAMESPACE

# Step 8: Display access information
echo -e "\n${BLUE}================================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${BLUE}================================================${NC}"

echo -e "\n${YELLOW}Access the application using one of these methods:${NC}"
echo -e "\n${BLUE}Option 1: Minikube Service (opens in browser)${NC}"
echo "  minikube service frontend-nodeport -n $NAMESPACE"
echo "  minikube service api-gateway-nodeport -n $NAMESPACE"

echo -e "\n${BLUE}Option 2: Port Forwarding${NC}"
echo "  kubectl port-forward svc/frontend-service 8080:8080 -n $NAMESPACE"
echo "  kubectl port-forward svc/api-gateway 5000:5000 -n $NAMESPACE"

echo -e "\n${BLUE}Option 3: Get Minikube Service URLs${NC}"
FRONTEND_URL=$(minikube service frontend-nodeport -n $NAMESPACE --url 2>/dev/null || echo "Run: minikube service frontend-nodeport -n $NAMESPACE --url")
API_URL=$(minikube service api-gateway-nodeport -n $NAMESPACE --url 2>/dev/null || echo "Run: minikube service api-gateway-nodeport -n $NAMESPACE --url")
echo "  Frontend: $FRONTEND_URL"
echo "  API Gateway: $API_URL"

echo -e "\n${BLUE}Useful commands:${NC}"
echo "  kubectl get pods -n $NAMESPACE          # Check pod status"
echo "  kubectl logs -f <pod-name> -n $NAMESPACE # View logs"
echo "  minikube dashboard                       # Open dashboard"
echo "  kubectl delete -k $SCRIPT_DIR            # Delete deployment"
