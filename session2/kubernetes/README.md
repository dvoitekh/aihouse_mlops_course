# Kubernetes Flask ML demo

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

### Build Docker image using Minikube Docker daemon so it can be used in k8s manifest

```bash
eval $(minikube docker-env)
docker build -t model-service:latest .
```

### Apply manifests to k8s

```bash
kubectl apply -f k8s/
```

### Test the endpoint in Kubernetes

Get a url to the service exposed by Minikube IP via the following command:

```bash
minikube service model-service-svc --url
```

```python
import requests
requests.post('<OUTPUT_OF_THE_PREVIOUS_COMMAND>/api/v1/predict', json={'prompts': ['i love you to the moon and back']}).json()
```


### k6 stress-testing

1. Install [k6 client](https://github.com/grafana/k6).

2. Perform stress-testing of the service via the following command

```bash
k6 run -u 2 -i 100 k6.js
```




