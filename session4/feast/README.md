# Feast Feature Store


## Install Redis via Helm chart:

Link to the [helm chart](https://artifacthub.io/packages/helm/bitnami/redis)

```bash
helm repo add my-repo https://charts.bitnami.com/bitnami
helm install helm-redis my-repo/redis --set auth.enabled=false --set replica.replicaCount=1
```

Now, we can port-forward Redis service to our machine:

```bash
tmux new -s redis
kubectl port-forward svc/helm-redis-master 6379:6379
```

Leave the tmux session and test the connectivity via [redis-cli](https://stackoverflow.com/a/25909402):

```bash
redis-cli
127.0.0.1:6379> set aa bb
127.0.0.1:6379> keys *
```

## Install Feast

Install dependencies:

```bash
pip install -r requirements.txt
```

Run demo Jupyter Notebook [with Feast examples](./Feast.ipynb)

Run Feast UI:

```bash
cd feature_store
feast ui -p 8000
```
