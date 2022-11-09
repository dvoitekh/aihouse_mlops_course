# Kubeflow Pipelines tutorial

## Prerequisites

Ensure that you have launched [Feast tutorial from this notebook](../../session4/feast/Feast.ipynb) and executed bottom cells below the "Prod Feature Store (we will use it for Kubeflow Pipelines)" title. This will prepare a Feast store for k8s.

Also, make sure that you have Istio port-forwarding enabled:

```bash
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create .env file:

```bash
cp .env.example .env
```

3. Build and push the pipeline:

```bash
eval $(minikube docker-env)
python3 pipeline.py
```

4. Navigate to Kubeflow UI to see job runs:

http://localhost:8080/_/pipeline/?ns=kubeflow-user-example-com#/runs


5. Access artifacts in Minio http://localhost:9000/minio/mlpipeline (minio/minio123):

```bash
kubectl port-forward svc/minio-service 9000:9000 -n kubeflow
```

6. Use Github actions to deploy pipeline automatically:

In case your server doesn't have a public IP, install [ngrok](https://ngrok.com/):

```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
sudo tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin
```

[Sign up](https://dashboard.ngrok.com/signup) and get auth token:

```bash
ngrok config add-authtoken <your-token>
```

Start the HTTP tunnel for istio gateway:

```bash
ngrok http 8080
```

Get the HTTPS link from the previous command's output and add it to your GitHub repo secrets: the url looks like this https://github.com/dvoitekh/aihouse_mlops_course/settings/secrets/actions.

Take a look at [the workflow file](../../.github/workflows/deploy_pipeline.yaml) and adjust it if needed. Now, you are ready to push the code to your repo and check if the pipeline runs successfully!
