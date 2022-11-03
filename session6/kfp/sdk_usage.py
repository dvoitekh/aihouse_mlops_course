import os

from dotenv import load_dotenv
from src.utils import get_kfp_client


if __name__ == '__main__':
    load_dotenv()
    experiment_name = os.environ["KUBEFLOW_EXPERIMENT_NAME"]
    pipeline_name = os.environ["KUBEFLOW_PIPELINE_NAME"]
    pipeline_version = os.environ["KUBEFLOW_PIPELINE_VERSION"]
    job_name = f"{pipeline_name}-{pipeline_version}"
    kubeflow_user = os.environ["KUBEFLOW_USER"]
    kubeflow_password = os.environ["KUBEFLOW_PASSWORD"]
    kubeflow_host = os.environ["KUBEFLOW_HOST"]
    kubeflow_namespace = os.environ["KUBEFLOW_NAMESPACE"]

    client = get_kfp_client(kubeflow_user, kubeflow_password, kubeflow_host, kubeflow_namespace)

    experiment = client.get_experiment(
        experiment_name=experiment_name,
        namespace=kubeflow_namespace
    )

    runs = [{'id': x.id, 'name': x.name,
             'status': x.status, 'error': x.error,
             'finished_at': x.finished_at, 'metrics': x.metrics}
            for x in client.list_runs(experiment_id=experiment.id, namespace=kubeflow_namespace).runs]

    print(runs)

    run = client.runs.get_run(run_id=runs[0]['id']).run

    print()
    print(run.id, run.name, run.metrics)
