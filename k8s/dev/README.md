# Kubernetes Deployment - Food Delivery Simulation App (Dev)

This directory contains Kubernetes manifests for deploying the Food Delivery Simulation application in a development environment using Minikube.

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/) installed
- [kubectl](https://kubernetes.io/docs/tasks/tools/) configured
- Docker installed

## Quick Start

### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192

# Enable ingress addon (optional)
minikube addons enable ingress
```

### 2. Build and Load Docker Images

Build images locally and load them into Minikube:

```bash
# Navigate to the project root
cd /path/to/fast-delivery-simulation-app

# Build all images
docker build -t api-gateway:latest ./api-gateway
docker build -t order-service:latest ./order-service
docker build -t delivery-service:latest ./delivery-service
docker build -t stock-service:latest ./stock-service
docker build -t metrics-service:latest ./metrics-service
docker build -t order-auto-generation-service:latest ./order-auto-generation-service
docker build -t tasks:latest ./tasks
docker build -t frontend-service:latest ./frontend-service

# Load images into Minikube
minikube image load api-gateway:latest
minikube image load order-service:latest
minikube image load delivery-service:latest
minikube image load stock-service:latest
minikube image load metrics-service:latest
minikube image load order-auto-generation-service:latest
minikube image load tasks:latest
minikube image load frontend-service:latest
```

### 3. Deploy the Application

```bash
# Deploy all resources using Kustomize
kubectl apply -k k8s/dev/

# Or preview what will be applied
kubectl kustomize k8s/dev/
```

### 4. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n fast-delivery-dev

# Watch pods until all are ready
kubectl get pods -n fast-delivery-dev -w
```

## Accessing the Application

### Option 1: Using Minikube Service (Recommended)

```bash
# Open frontend in browser
minikube service frontend-nodeport -n fast-delivery-dev

# Open API gateway in browser
minikube service api-gateway-nodeport -n fast-delivery-dev
```

### Option 2: Using Minikube Tunnel

```bash
# Start minikube tunnel (run in a separate terminal)
minikube tunnel

# Access via NodePort
# Frontend: http://localhost:30808
# API Gateway: http://localhost:30500
```

### Option 3: Port Forwarding

```bash
# Frontend
kubectl port-forward svc/frontend-service 8080:8080 -n fast-delivery-dev

# API Gateway
kubectl port-forward svc/api-gateway 5000:5000 -n fast-delivery-dev
```

### Option 4: Using Ingress

1. Enable ingress addon:
   ```bash
   minikube addons enable ingress
   ```

2. Get Minikube IP and add to `/etc/hosts`:
   ```bash
   echo "$(minikube ip) fast-delivery.local" | sudo tee -a /etc/hosts
   ```

3. Access:
   - Frontend: http://fast-delivery.local
   - API: http://fast-delivery.local/api

## Monitoring

```bash
# Check pod status
kubectl get pods -n fast-delivery-dev

# Check services
kubectl get svc -n fast-delivery-dev

# View logs
kubectl logs -f deployment/api-gateway -n fast-delivery-dev
kubectl logs -f deployment/order-service -n fast-delivery-dev
kubectl logs -f deployment/celery-worker -n fast-delivery-dev

# Describe a pod for troubleshooting
kubectl describe pod <pod-name> -n fast-delivery-dev

# Open Minikube dashboard
minikube dashboard
```

## Cleanup

```bash
# Delete all resources
kubectl delete -k k8s/dev/

# Or delete namespace (removes everything)
kubectl delete namespace fast-delivery-dev

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Troubleshooting

### Images not found
Make sure you loaded images into Minikube:
```bash
minikube image ls | grep -E "api-gateway|order-service|delivery-service|stock-service"
```

### Pods stuck in Pending
Check if there are enough resources:
```bash
kubectl describe pod <pod-name> -n fast-delivery-dev
minikube ssh -- df -h  # Check disk space
```

### Database connection issues
Wait for MySQL to be fully ready:
```bash
kubectl wait --for=condition=ready pod -l app=mysql -n fast-delivery-dev --timeout=120s
```

### Reset and redeploy
```bash
kubectl delete -k k8s/dev/
kubectl apply -k k8s/dev/
```

## Architecture

```
                    ┌─────────────────┐
                    │    Ingress      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              │
    ┌─────────────────┐ ┌──────────────┐   │
    │  Frontend (Vue) │ │  API Gateway │   │
    └─────────────────┘ └──────┬───────┘   │
                               │           │
         ┌─────────────────────┼───────────┼───────────────────┐
         │                     │           │                   │
         ▼                     ▼           ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Order Service  │ │Delivery Service │ │  Stock Service  │ │ Metrics Service │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │                   │
         └─────────┬─────────┴─────────┬─────────┘                   │
                   │                   │                             │
                   ▼                   ▼                             ▼
             ┌──────────┐       ┌──────────┐                  ┌──────────┐
             │  MySQL   │       │  Redis   │                  │ InfluxDB │
             └──────────┘       └──────────┘                  └──────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Celery Worker  │
                            └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │Order Auto Gen   │
                            └─────────────────┘
```

## Manifest Files

| File | Description |
|------|-------------|
| `namespace.yaml` | Creates the `fast-delivery-dev` namespace |
| `configmap.yaml` | Application configuration |
| `secrets.yaml` | Database passwords and tokens |
| `mysql-init-configmap.yaml` | MySQL initialization SQL |
| `pvc.yaml` | Persistent Volume Claims for databases |
| `mysql.yaml` | MySQL database deployment |
| `redis.yaml` | Redis cache/queue deployment |
| `influxdb.yaml` | InfluxDB time-series database |
| `order-service.yaml` | Order management service |
| `delivery-service.yaml` | Delivery management service |
| `stock-service.yaml` | Stock/inventory service |
| `metrics-service.yaml` | Metrics collection service |
| `celery-worker.yaml` | Background task workers |
| `order-auto-generation.yaml` | Order simulation service |
| `api-gateway.yaml` | API Gateway/Router |
| `frontend.yaml` | Vue.js frontend |
| `ingress.yaml` | Ingress + NodePort services |
| `kustomization.yaml` | Kustomize configuration |
