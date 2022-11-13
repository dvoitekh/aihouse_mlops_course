# Kale notebooks

[Kale](https://github.com/kubeflow-kale/kale) can be used for fast prototyping of Kubeflow Pipelines via Jupyter Notebooks.

## How to run

1. Start a new Kubeflow Jupyter Notebook with this custom Docker Image `gcr.io/arrikto/jupyter-kale:v0.5.0`.

2. Open the JupyterLab of the created notebook and clone our repo to the home directory:

```bash
git clone https://github.com/dvoitekh/aihouse_mlops_course.git
```

3. In the Finder tab on the left navigate to the directory `aihouse_mlops_course/session6/kale`

4. Open the `titanic_dataset_ml.ipynb` notebook

5. Run the first cell with `pip install ...`

6. Open a Kale plugin by clicking one the blue icon on the left

7. Build and upload the pipeline to Kubeflow

8. Now, you should be able to see the new pipeline in the KFP UI
