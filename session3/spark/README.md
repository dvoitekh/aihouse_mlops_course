## Spark on Kubernetes

This tutorial describes the process of configuring Spark in Kubernetes via Spark Operator. Also, the sample job reads and processes files from s3.

## How to install

The following steps are based on the [official Spark on Kubernetes overview](https://spark.apache.org/docs/3.2.1/running-on-kubernetes.html)

1. Make sure that you have git-lfs installed and that you pulled all the files:

```bash
sudo apt-get install git-lfs
git lfs pull
```

2. Install aws-cli:

```bash
pip install awscli==1.26.4
```

3. Download and unpack Apache Spark from [the official page](https://spark.apache.org/downloads.html). For instance:

```bash
wget https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz
tar -xvf spark-3.3.1-bin-hadoop3.tgz
```

3. Build Docker images (Spark + PySpark) that will be used as a base to submit Spark jobs to k8s. This command will also add the image to the Minikube context:

```bash
eval $(minikube docker-env)
cd spark-3.3.1-bin-hadoop3
./bin/docker-image-tool.sh -m -t v3.3.1 -p ./kubernetes/dockerfiles/spark/bindings/python/Dockerfile build
docker images | grep spark
```

4. Now, you're ready to submit Spark tasks to k8s. For this you need to get the IP of the k8s API server and then, for instance, start the spark shell (you can make sure that resources are allocated by opening Minikube dashboard):

```bash
export K8S_SERVER=$(kubectl config view --output=jsonpath='{.clusters[].cluster.server}')
./bin/spark-shell \
  --master k8s://$K8S_SERVER \
  --conf spark.kubernetes.container.image=spark:v3.3.1 \
  --conf spark.kubernetes.context=minikube \
  --conf spark.kubernetes.namespace=default \
  --verbose
```

## Demo job

1. Data

    The job relies on data located in Minio.

    You deploy Minio to k8s [via helm chart](https://artifacthub.io/packages/helm/bitnami/minio):

    ```bash
    helm repo add my-repo https://charts.bitnami.com/bitnami
    helm install helm-minio my-repo/minio --set auth.rootUser=minioadmin --set auth.rootPassword=minioadmin
    ```

    And don't forget to `port-forward` the Minio service via so we can seed it with data:
    ```bash
    kubectl port-forward svc/helm-minio 9000:9000 9001:9001
    ```

    You can seed Minio with data using [awscli](https://pypi.org/project/awscli/):
    ```bash
    AWS_ACCESS_KEY_ID=minioadmin AWS_SECRET_ACCESS_KEY=minioadmin aws --endpoint-url http://localhost:9000 s3 mb s3://data
    AWS_ACCESS_KEY_ID=minioadmin AWS_SECRET_ACCESS_KEY=minioadmin aws --endpoint-url http://localhost:9000 s3 cp ../data/ s3://data/ --recursive
    AWS_ACCESS_KEY_ID=minioadmin AWS_SECRET_ACCESS_KEY=minioadmin aws --endpoint-url http://localhost:9000 s3 ls s3://data
    ```

2. Install [Spark Operator](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/quick-start-guide.md) via helm chart:
    ```bash
    helm repo add spark-operator https://googlecloudplatform.github.io/spark-on-k8s-operator
    helm install helm-spark spark-operator/spark-operator --namespace spark-operator --create-namespace
    ```

    As mentioned [here](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/issues/1314#issuecomment-892916095), also need to create a service account for jobs. Create it by running:
    ```bash
    kubectl apply -f spark-service-account.yaml
    ```

3. Now, we need to build a Docker image for our job:

    ```bash
    eval $(minikube docker-env)
    docker build -t spark-job:latest .
    ```

4. Deploy the job:

    ```bash
    kubectl apply -f spark-job.yaml
    ```

5. After a while find a pod of the corresponding k8s job driver and check the logs for execution results:

    ```bash
    kubectl get po | grep spark-job
    kubectl logs -f spark-job-driver
    AWS_ACCESS_KEY_ID=minioadmin AWS_SECRET_ACCESS_KEY=minioadmin aws --endpoint-url http://localhost:9000 s3 ls s3://data/output/
    ```
