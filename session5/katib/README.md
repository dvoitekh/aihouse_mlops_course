# Katib HPO tutorial

1. Prepare (Kaggle Facial Expressions dataset)[https://www.kaggle.com/datasets/jonathanoheix/face-expression-recognition-dataset]:

Go to (your Kaggle account)[https://www.kaggle.com/dvoitekh/account] and get .json credentials.

```bash
chmod 600 ~/.kaggle/kaggle.json
pip install kaggle
kaggle datasets download jonathanoheix/face-expression-recognition-dataset
unzip face-expression-recognition-dataset.zip
rm -rf images/images
rm face-expression-recognition-dataset.zip
```

(Optional) Leave only small dataset of the dataset (delete all files with names longer than 7 chars):

```bash
find ./images/ -type f -regextype posix-egrep -regex '.*[^/]{8}' -delete
```

2. Build Katib experiment image:

```bash
docker build -t katib-experiment:1.0 .
```

3. Launch experiment:

```bash
kubectl apply -f experiment.yaml
```

4. Track experiment via kubectl:

```bash
kubectl get po -n kubeflow-user-example-com
kubectl logs -f pytorch-facial-emotions-***-*** -n kubeflow-user-example-com metrics-logger-and-collector
```

5. Also, navigate to (Kubeflow AutoML UI)[http://localhost:8080/_/katib/?ns=kubeflow-user-example-com] to view detailed report
