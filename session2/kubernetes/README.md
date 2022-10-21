# Kubernetes Flask ML demo

### Forward Minikube Docker daemon

```bash
eval $(minikube docker-env)
```

### Build Docker image

```bash
docker build -t model-service:latest .
```

### Run the Docker image locally

```bash
docker run -p 5000:5000 model-service:latest
```

### Perform requests to the container

```python
import requests
requests.post('http://localhost:5000/api/v1/predict', json={'prompts': ['i love you to the moon and back']}).json()
```

### Apply manifests to k8s

```bash
kubectl apply -f k8s/
```

### Forward k8s service to your local machine and test some requests

```bash
kubectl port-forward svc/model-service-svc 5000:5000
```


### k6 stress-testing

1. Install [k6 client](https://github.com/grafana/k6).

2. Perform stress-testing of the service via the following command

```bash
k6 run -u 2 -i 100 k6.js
```




