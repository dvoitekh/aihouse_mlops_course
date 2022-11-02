# Kubeflow Pipelines tutorial

## Prerequisites

Ensure that you have launched [Feast tutorial from this notebook](../../session4/feast/Feast.ipynb) and executed bottom cells below the "Prod Feature Store (we will use it for Kubeflow Pipelines)" title. This will prepare a Feast store for k8s.

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
