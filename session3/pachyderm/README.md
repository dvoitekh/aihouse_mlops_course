## Pachyderm


## How to start

1. Install [Pachyderm](https://docs.pachyderm.com/2.3.x/getting-started/local-installation/):

Install pachctl client:

```bash
curl -o /tmp/pachctl.tar.gz -L https://github.com/pachyderm/pachyderm/releases/download/v2.3.6/pachctl_2.3.6_linux_amd64.tar.gz && tar -xvf /tmp/pachctl.tar.gz -C /tmp && sudo cp /tmp/pachctl_2.3.6_linux_amd64/pachctl /usr/local/bin
pachctl version --client-only
```

Install pachyderm via helm chart:

```bash
helm repo add pach https://helm.pachyderm.com
helm repo update
kubectl create namespace pachyderm
helm install --wait --timeout 10m pachd pach/pachyderm --set deployTarget=LOCAL --namespace pachyderm
kubectl get pods -n pachyderm
```

Connect it to the client:

```bash
pachctl config import-kube local --overwrite
pachctl config set active-context local
```

Perform port-forward in tmux session:

```bash
pachctl port-forward --namespace pachyderm
```

Now you can execute commands like:

```bash
pachctl list repo
```

2. Go to [notebooks](./notebooks/) directory and either run the Intro notebook, or the custom Pachyderm project with multiple pipelines

