# Kubeflow tutorials

## Kubeflow installation

1. Prerequisites

Install kustomize v3.2.0

```bash
wget https://github.com/kubernetes-sigs/kustomize/releases/download/v3.2.0/kustomize_3.2.0_linux_amd64
sudo install -o root -g root -m 0755 kustomize_3.2.0_linux_amd64 /usr/local/bin/kustomize
kustomize --help
```

IMPORTANT! Make sure that you increased [ulimit](https://github.com/kubernetes/kubernetes/issues/74551#issuecomment-910520361) and [inotify values](https://github.com/kubeflow/manifests/issues/2087#issuecomment-1101482095). Otherwise the deployment will fail.

2. Clone [Kubeflow manifests](https://github.com/kubeflow/manifests) repo and install Kubeflow v.1.5.1 via `kustomize`:

```bash
git clone https://github.com/kubeflow/manifests.git
cd manifests
git checkout v1.5-branch
while ! kustomize build example | kubectl apply -f -; do echo "Retrying to apply resources"; sleep 10; done
```

3. Make sure that all new pods are up and running:

```bash
kubectl get po --all-namespaces
```

4. In order to access Kubeflow dashboard and API:

Port-forward istio gateway to localhost in a separate tmux session:

```bash
tmux new -s istio
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

NOTE: you can also use nodeport provided via Minikube gateway (port 31711):

```bash
minikube service istio-ingressgateway -n istio-system --url
```

5. Access the Kubeflow dashboard via http://localhost:8080 (Dex credentials: `user@example.com`/`12341234`)
