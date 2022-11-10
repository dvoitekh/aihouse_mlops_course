# Seldon Core tutorial

## Prerequisites

Ensure that you have launched [Feast tutorial from this notebook](../../session4/feast/Feast.ipynb) and executed bottom cells below the "Prod Feature Store (we will use it for Kubeflow Pipelines)" title. This will prepare a Feast store for k8s.


## Seldon-core operator installation via Kubeflow extension

Considering that you already have Kubeflow up and running:

```bash
git clone https://github.com/kubeflow/manifests.git
cd contrib/seldon
kustomize build seldon-core-operator/base | kubectl apply -n kubeflow -f -
kubectl get po -n kubeflow | grep seldon
```

## First Seldon service deployment and usage

Install required packages:

```bash
pip install -r requirements.txt
```

### Kubeflow Istio Gateway

The official integration guide with Kubeflow can be found [here](https://www.kubeflow.org/docs/external-add-ons/serving/seldon/).

Create a separate namespace where our Seldon services will be running:

```bash
kubectl create namespace seldon
kubectl label namespace seldon serving.kubeflow.org/inferenceservice=enabled
```

Deploy a sample Seldon classifier:

```bash
kubectl apply -f k8s/mock_classifier.yaml
```

Assuming that you already have svc/istio-ingressgateway forwarded to your local machine on port 8080 you can now perform requests.
Note: by default, [Dex Auth is required in order to access the KFP API from the outside of the cluster](https://stackoverflow.com/a/72358528)

```python
import requests


def get_kubeflow_session_cookie(username, password, host):
    session = requests.Session()
    response = session.get(host)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"login": username, "password": password}

    session.post(response.url, headers=headers, data=data)
    return session.cookies.get_dict()["authservice_session"]

session_cookie = get_kubeflow_session_cookie('user@example.com', '12341234', 'http://localhost:8080')

requests.post(
    'http://localhost:8080/seldon/seldon/seldon-model/api/v1.0/predictions',
    json={"data": {"ndarray":[[1., 1., 1., 1.]]}}, cookies={'authservice_session': session_cookie}
).json()
```

### Standalone Seldon service

Alternatively, you can port-forward a dedicated Seldon service of the app:

```bash
kubectl port-forward svc/seldon-model-example-classifier -n seldon 9005:9000 9500:9500
```

REST endpoint:

```python
import requests
requests.post('http://localhost:9005/api/v1.0/predictions', json={"data":{"ndarray": [[1., 1., 1., 1.]]}}).json()
```

GRPC endpoint:

```python
import grpc
from google.protobuf import struct_pb2
from seldon_core.proto import prediction_pb2, prediction_pb2_grpc

channel = grpc.insecure_channel(f"localhost:9500")
stub = prediction_pb2_grpc.ModelStub(channel)

batch = struct_pb2.ListValue()
batch.append([1., 1., 1., 1.])
data = prediction_pb2.DefaultData(ndarray=batch)
seldon_request = prediction_pb2.SeldonMessage(data=data)
response = stub.Predict(seldon_request)
response
```

## Advanced Seldon Tutorial

### Prerequisites

Ensure that you have Minio and Feast feature store configured and filled with data according to the [Feast tutorial notebook](../../session4/feast/Feast.ipynb)

### How to run a SKLearn-server based service

Add sklearn model to Minio bucket:

```bash
AWS_ACCESS_KEY_ID=minioadmin AWS_SECRET_ACCESS_KEY=minioadmin aws --endpoint-url http://localhost:9000 s3 cp checkpoints/model.joblib s3://data/models/
```

Deploy k8s secret with minio credentials:

```bash
kubectl apply -f k8s/seldon_minio_secret.yaml
```

Deploy the actual Seldon service:

```bash
kubectl apply -f k8s/sklearn_deployment.yaml
```

Port-forward the Seldon service:

```bash
kubectl port-forward svc/housing-regressor-sklearn-default-regressor -n seldon 9005:9000 9500:9500
```

Perform request to the service:

```bash
curl -X POST \
  http://localhost:9005/api/v1.0/predictions \
  -H 'Content-Type: application/json' \
  -d '{"data":{"ndarray":[[1,1,1,1,1,1,1,1,1]]}}'
```

Optional. If you want to test it without k8s in Docker locally (can be used for tests as well):

```
docker run -p 9005:9000 -e PREDICTIVE_UNIT_PARAMETERS='[{"type":"STRING","name":"model_uri","value":"file:///model"}, {"type":"STRING","name":"method","value":"predict"}]' -v ${PWD}/checkpoints:/model seldonio/sklearnserver:1.14.1
```

### Jaeger and Prometheus monitoring

Before we go to the deployment of more complex Seldon pipelines, let's deploy useful monitoring tools supported by Seldon.

Let's install Jaeger first. For this we can install the [jaeger-operator](https://www.jaegertracing.io/docs/1.35/operator/#installing-the-operator-on-kubernetes):

```bash
kubectl create namespace observability
kubectl create -f https://github.com/jaegertracing/jaeger-operator/releases/download/v1.35.0/jaeger-operator.yaml -n observability
```

And now we can deploy all-in-one minimalistic Jaeger deployment:

```bash
kubectl create namespace jaeger
kubectl apply -f k8s/jaeger.yaml
```

Port-forward Jaeger UI in tmux session:

```bash
kubectl port-forward svc/jaeger-query -n jaeger 16686:16686
```

We can also deploy Prometheus stack and Grafana:

[Prometheus Helm chart](https://docs.seldon.io/projects/seldon-core/en/latest/analytics/analytics.html):

```bash
kubectl create namespace seldon-monitoring

helm upgrade --install seldon-monitoring kube-prometheus \
    --version 6.9.5 \
    --set fullnameOverride=seldon-monitoring \
    --namespace seldon-monitoring \
    --repo https://charts.bitnami.com/bitnami
```

Port-forward a Prometheus dashboard in tmux session:

```bash
kubectl port-forward svc/seldon-monitoring-prometheus -n seldon-monitoring 9090:9090
```

In order to collect Seldon metrics, we'll deploy a PodMonitor:

```bash
kubectl apply -f k8s/seldon_podmonitor.yaml
```

And let's install [Grafana from a Helm chart](https://artifacthub.io/packages/helm/grafana/grafana):

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install helm-grafana grafana/grafana
```

And get a password for the dashboard via:

```bash
kubectl get secret --namespace default helm-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

Port-forward Grafana in tmux and navigate to the corresponding url in the browser:

```bash
kubectl port-forward svc/helm-grafana 8000:80
```

### How to deploy Python-based components

1. Build the base docker image for Seldon services:

```bash
eval $(minikube docker-env)
docker build -t seldon-base:1.0.0 .
```

2. Deploy a preprocessor service for our Housing Regresion problem (based on Feast online store):

```bash
kubectl apply -f k8s/python_preprocessor.yaml
kubectl get po -n seldon
```

Port-forward the corresponding service:

```bash
kubectl port-forward svc/housing-preprocessor-model-model -n seldon 9005:9000
```

And perform request to get normalized features for given HouseIds:

```bash
curl -X POST \
  http://localhost:9005/api/v1.0/predictions \
  -H 'Content-Type: application/json' \
  -d '{"data":{"ndarray":[[1], [5]]}}'
```

3. Deploy a regression model based on Python component:

```bash
kubectl apply -f k8s/python_regressor.yaml
kubectl get po -n seldon
```

Port-forward the corresponding service:

```bash
kubectl port-forward svc/housing-regressor-model-model -n seldon 9005:9000
```

And perform request to get price prediction for given features:

```bash
curl -X POST \
  http://localhost:9005/api/v1.0/predictions \
  -H 'Content-Type: application/json' \
  -d '{"data":{"ndarray":[[-1.7319668924113674,-0.7324396877792114,-0.3686446776412593,-0.7979812453599388,0.07906991444149086,0.7289808981819601,0.08193376858427932,-0.6797418814172994,0.5938194097272528],[-1.7312955548882658,-1.3334053246300217,-0.8453931491070594,-0.34815492500568834,-0.019726266386578314,1.1316531272558914,-0.018082498363888314,1.6377819950507821,-0.9834354838678211]]}}'
```

4. Deploy preprocessor-regressor pipeline:

```bash
kubectl apply -f k8s/python_pipeline.yaml
kubectl get po -n seldon
```

Port-forward the corresponding pipeline service:

```bash
kubectl port-forward svc/housing-pipeline-model -n seldon 8005:8000
```

And perform request to get price predictions based on HouseIds:

```bash
curl -X POST \
  http://localhost:8005/api/v1.0/predictions \
  -H 'Content-Type: application/json' \
  -d '{"data":{"ndarray":[[1], [5]]}}'
```

See how Seldon creates service for every container:

```bash
kubectl get svc -n seldon | grep pipeline
```

5. Deploy preprocessor-regressor-ood-combiner pipeline:

```bash
kubectl apply -f k8s/python_pipeline_combiner.yaml
kubectl get po -n seldon
```

Port-forward the corresponding pipeline service:

```bash
kubectl port-forward svc/housing-pipeline-combiner-combiner -n seldon 8005:8000
```

And perform request to get price predictions based on HouseIds:

```bash
curl -X POST \
  http://localhost:8005/api/v1.0/predictions \
  -H 'Content-Type: application/json' \
  -d '{"data":{"ndarray":[[154], [5]]}}'
```

Notice how Seldon creates service for every container:

```bash
kubectl get svc -n seldon | grep pipeline
```

6. Deploy standard AB test:

```bash
kubectl apply -f k8s/python_ab_test_standard.yaml
kubectl get po -n seldon
```

Port-forward the corresponding pipeline service:

```bash
kubectl port-forward svc/housing-standard-ab-test-ab-test -n seldon 8005:8000
```

Perform multiple requests to get price predictions based on HouseIds from different models:

```bash
curl -X POST \
  http://localhost:8005/api/v1.0/predictions \
  -H 'Content-Type: application/json' \
  -d '{"data":{"ndarray":[[154], [5]]}}'
```

See how Seldon balances the traffic between 2 models.

7. Deploy a custom AB test:

```bash
kubectl apply -f k8s/python_ab_test_custom.yaml
kubectl get po -n seldon
```

Port-forward the corresponding pipeline service:

```bash
kubectl port-forward svc/housing-router-ab-test-router -n seldon 8005:8000
```

Perform multiple requests to get price predictions based on HouseIds from different models:

```bash
curl -X POST \
  http://localhost:8005/api/v1.0/predictions \
  -H 'Content-Type: application/json' \
  -d '{"data":{"ndarray":[[154], [5]]}}'
```

See how Seldon balances the traffic between 2 models.

8. Send feedback to the model:

```bash
curl -X POST \
  http://localhost:8005/api/v1.0/feedback \
  -H 'Content-Type: application/json' \
  -d '{"request": {"data": {"ndarray":[[154], [5]]}}, "response": {"data": {"names":[], "ndarray": [0.875,0.596]}}, "reward": -1, "truth": {"data": {"ndarray": [1, 1]}}}'
```

See [this reference](https://github.com/SeldonIO/seldon-core/blob/6c7a322267af2769df097b8546aaaf40c18c4794/components/routers/epsilon-greedy/EpsilonGreedy.py#L119) how to implement a feedback loop.

7. Tests

Install the project as a Python package:

```bash
pip install .[test]
```

Run the Regressor service in a local Docker container. IMPORTANT: make sure you're not in the Minikube context:

```bash
docker run -p 9005:9000 -p 5005:5000 -e MODEL_NAME='src.Regressor' seldon-base:1.0.0
```

Run model, integration, and unit tests:

```bash
pytest tests/
```
