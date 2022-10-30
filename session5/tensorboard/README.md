# Jupyter Notebooks and Tensorboard in Kubeflow

## Use custom Jupyter Notebook Docker image

1. Build image inside Minikube Docker runtime:

```bash
eval $(minikube docker-env)
docker build -t kubeflow-jupyter-custom:1.0 .
```

2. Run this custom Docker image from the Kubeflow Jupyter dashboard (P.S. do not forget to use PullPolicy='Never')

3. Copy (BasicTensorboard.ipynb)[./BasicTensorboard.ipynb] notebook to the launched JupyterLab

4. Create (a new Kubeflow Tensorboard)[http://localhost:8080/_/tensorboards/?ns=kubeflow-user-example-com]. Make sure that you selected a PVC of your notebook server and specified the `runs` directory in the path input.

5. For more sophisticated example with real training run (FacialEmotionsTrainingTensorboard.ipynb)[./FacialEmotionsTrainingTensorboard.ipynb]
