# DevOps Project: Poker Session Logging Application

## Introduction

This repository contains a simple Poker Session Logging Application designed to demonstrate various DevOps practices, including containerization, orchestration, monitoring, and CI/CD. The main goal is to showcase a basic application and the implementation of DevOps tools and workflows around it.

## Features

- **FastAPI Application**: A RESTful API to log poker sessions.
- **Dockerized**: The application is containerized using Docker.
- **Kubernetes**: Deployment on a local Minikube cluster using Kubernetes.
- **Helm Charts**: Kubernetes manifests converted to Helm charts for easier deployment.
- **Monitoring**: Integration with Prometheus for monitoring and Grafana for visualization.
- **CI/CD**: Automated CI/CD pipeline using GitHub Actions.

## Setup Instructions

### Prerequisites

- Docker
- Minikube
- kubectl
- Helm
- GitHub account (for CI/CD)

### FastAPI Application

1. Clone the repository:
    ```sh
    git clone https://github.com/SkanderGhariani/devops-project.git
    cd devops-project
    ```

2. Build and run the Docker container:
    ```sh
    docker build -t poker-session-app .
    docker run -p 8000:8000 poker-session-app
    ```

### Kubernetes Deployment

1. Start Minikube:
    ```sh
    minikube start
    ```

2. Deploy the application using Helm:
    ```sh
    helm install poker-app helm/poker-app
    ```

3. Forward the service port to access the application:
    ```sh
    kubectl port-forward svc/poker-session-service -n poker-app 8000:80 &
    ```

### Prometheus and Grafana Setup

1. Deploy Prometheus and Grafana using Helm:
    ```sh
    helm install prometheus stable/prometheus
    helm install grafana stable/grafana
    ```

2. Forward the service ports to access Prometheus and Grafana:
    - Prometheus:
      ```sh
      kubectl port-forward svc/prometheus-server -n poker-app 9090:80
      ```
    - Grafana:
      ```sh
      kubectl port-forward svc/grafana 3000:80 -n poker-app
      ```

### Monitoring and Alerting

1. Configure Prometheus with alerting rules:
    ```yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: prometheus-alert-rules
      namespace: poker-app
    data:
      alerting_rules.yaml: |
        groups:
          - name: example
            rules:
            - alert: HighErrorRate
              expr: rate(http_requests_total{status=~"4..|5.."}[1m]) > 0.05
              for: 1m
              labels:
                severity: page
              annotations:
                summary: "High error rate detected"
                description: "High error rate detected for the past 1 minutes."
    ```

2. Apply the ConfigMap:
    ```sh
    kubectl apply -f path/to/alerting_rules.yaml
    ```

### CI/CD Pipeline

1. GitHub Actions workflow is set up to automate testing and deployment. On every push, the workflow will:
    - Build and test the Docker image
    - Push the image to Docker Hub
    - Deploy the application to the Minikube cluster

2. To view and customize the workflow, check `.github/workflows/ci-cd.yml` in the repository.

## Conclusion

This project demonstrates the implementation of a simple application with various DevOps tools and practices. Feel free to explore the repository and use it as a reference for your DevOps learning journey.
