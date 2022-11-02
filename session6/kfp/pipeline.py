import kfp
import os
import subprocess
import kfp.dsl as dsl
import kfp.components as comp
from dotenv import load_dotenv

from kfp.components import InputPath, OutputPath, create_component_from_func

from src.utils import get_kfp_client, generate_env_secret_variable


load_dotenv()


def notification(namespace: str, run_id: str, pipeline_name: str, status, duration: str, failures: str):
    print(f"""
        <http//:localhost:8080/_/pipeline/?ns={namespace}#/runs/details/{run_id}|Pipeline {pipeline_name}> status: {status}\n
        Duration: {duration} seconds\n
        Failures: {failures}
    """)


def dataset_generation(dataset_path: OutputPath('Dataset')):
    import os
    import pandas as pd
    import feast
    from feast.infra.offline_stores.file_source import SavedDatasetFileStorage

    store = feast.FeatureStore('.')

    entity_df = pd.DataFrame.from_dict({"HouseId": [i for i in range(1, 20641)]})
    entity_df['event_timestamp'] = pd.to_datetime('now', utc=True)

    retrieval_job = store.get_historical_features(
        entity_df=entity_df,
        features=[
            "house_main_view:MedInc",
            "house_main_view:HouseAge",
            "house_main_view:AveRooms",
            "house_main_view:AveBedrms",
            "house_main_view:Population",
            "house_main_view:AveOccup",
            "house_main_view:MedHouseVal",
            "house_lat_lon_view:Latitude",
            "house_lat_lon_view:Longitude",
        ],
    )
    df = retrieval_job.to_df().drop(columns=['event_timestamp'])

    print('Dataset generation completed')
    df.to_csv(dataset_path, index=False)


def dataset_validation(dataset_path: InputPath('Dataset'), mlpipeline_ui_metadata_path: OutputPath()):
    import pandas as pd
    import json
    from pandas_profiling import ProfileReport

    df = pd.read_csv(dataset_path)
    profile = ProfileReport(df, title="Dataset Profiling Report")

    with open(mlpipeline_ui_metadata_path, 'w') as f:
        json.dump({
            'outputs': [{
                'storage': 'inline',
                'source': profile.to_html(),
                'type': 'web-app',
            }]
        }, f)


def training(dataset_path: InputPath('Dataset'),
             model_path: OutputPath('DecisionTreeRegressor'),
             mlpipeline_metrics_path: OutputPath('Metrics')):
    import pandas as pd
    import numpy as np
    import json
    from sklearn.tree import DecisionTreeRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_validate
    from joblib import dump

    TARGET_COLUMN = 'MedHouseVal'

    df = pd.read_csv(dataset_path)
    X, y = df.drop(columns=[TARGET_COLUMN]), df[TARGET_COLUMN]

    print(f"Train features: {X.columns}")

    scaler = StandardScaler()
    X_transformed = scaler.fit_transform(X)
    y_log = np.log(y)

    regressor = DecisionTreeRegressor()
    cv_scores = cross_validate(estimator=regressor, X=X_transformed, y=y_log, cv=10,
                               scoring=('r2', 'neg_mean_squared_error'))
    regressor.fit(X_transformed, y_log)

    dump(regressor, model_path)
    # dump(scaler, f'{dataset_path}/preprocessing.joblib')

    with open(mlpipeline_metrics_path, 'w') as f:
        json.dump({
            'metrics': [{
                'name': 'cv-mean-r-squared',
                'numberValue': cv_scores['test_r2'].mean(),
                'format': "RAW",
            }, {
                'name': 'cv-mean-neg-mean-sq-error',
                'numberValue': cv_scores['test_neg_mean_squared_error'].mean(),
                'format': "RAW",
            }]
        }, f)


def evaluation(model_path: InputPath('DecisionTreeRegressor')):
    from joblib import load
    model = load(model_path)


@dsl.pipeline(name='House Pricing Pipeline', description='')
def pipeline():
    base_image = docker_image_name = os.environ["EXECUTOR_DOCKER_IMAGE"]
    docker_image_pull_policy = os.environ["EXECUTOR_DOCKER_IMAGE_PULL_POLICY"]

    # Use persistent volume (deprecated) in case you need to share multiple heavy files between components:
    # vop = dsl.VolumeOp(
    #     name="pipeline-pvc", resource_name="data-volume", modes=dsl.VOLUME_MODE_RWO, size="1Gi"
    # )
    # .add_pvolumes({'/tmp': vop.volume}) \

    notification_op = comp.func_to_container_op(notification,
                                                base_image=base_image,
                                                packages_to_install=[],
                                                output_component_file='components/notification.yaml')
    dataset_generation_op = comp.func_to_container_op(dataset_generation,
                                                      base_image=base_image,
                                                      packages_to_install=['feast[aws,redis]==0.26.0'],
                                                      output_component_file='components/dataset_generation.yaml')
    dataset_validation_op = comp.func_to_container_op(dataset_validation,
                                                      base_image=base_image,
                                                      packages_to_install=['pandas-profiling==3.4.0'],
                                                      output_component_file='components/dataset_validation.yaml')
    training_op = comp.func_to_container_op(training,
                                            base_image=base_image,
                                            packages_to_install=[],
                                            output_component_file='components/training.yaml')
    evaluation_op = comp.func_to_container_op(evaluation,
                                              base_image=base_image,
                                              packages_to_install=[],
                                              output_component_file='components/evaluation.yaml')

    # access Argo variables https://github.com/argoproj/argo-workflows/blob/master/docs/variables.md#global
    notification_step = notification_op(
        namespace="{{workflow.namespace}}",
        run_id="{{workflow.uid}}",
        pipeline_name="{{workflow.name}}",
        status="{{workflow.status}}",
        duration="{{workflow.duration}}",
        failures="{{workflow.failures}}"
    ).add_resource_request('memory', '500Mi') \
     .add_resource_request('cpu', '500m') \
     .add_resource_limit('memory', '500Mi') \
     .add_resource_limit('cpu', '500m') \
     .set_image_pull_policy(docker_image_pull_policy)

    with dsl.ExitHandler(notification_step):
        dataset_generation_step = dataset_generation_op().add_resource_request('memory', '500Mi') \
                                                         .add_resource_request('cpu', '500m') \
                                                         .add_resource_limit('memory', '500Mi') \
                                                         .add_resource_limit('cpu', '500m') \
                                                         .set_image_pull_policy(docker_image_pull_policy)

        dataset_validation_step = dataset_validation_op(dataset_generation_step.output).add_resource_request('memory', '500Mi') \
                                                                                       .add_resource_request('cpu', '500m') \
                                                                                       .add_resource_limit('memory', '1000Mi') \
                                                                                       .add_resource_limit('cpu', '1000m')

        training_step = training_op(dataset_generation_step.output).add_resource_request('memory', '500Mi') \
                                                                   .add_resource_request('cpu', '500m') \
                                                                   .add_resource_limit('memory', '1000Mi') \
                                                                   .add_resource_limit('cpu', '1000m') \
                                                                   .set_image_pull_policy(docker_image_pull_policy)

        evaluation_step = evaluation_op(training_step.outputs['model']).add_resource_request('memory', '500Mi') \
                                                                       .add_resource_request('cpu', '500m') \
                                                                       .add_resource_limit('memory', '1000Mi') \
                                                                       .add_resource_limit('cpu', '1000m') \
                                                                       .set_image_pull_policy(docker_image_pull_policy)

    #   In case you have custom node with taints: https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/#concepts
    #   from kubernetes.client import V1Toleration
    #   .add_toleration(V1Toleration(effect='NoSchedule',
    #                                key='gpu',
    #                                operator='Equal',
    #                                value='ml'))

    #   Add env variables:
    #   .add_env_variable(generate_env_secret_variable("REDSHIFT_CONNECTION_STRING", "capstone-secrets", "redshift-connection-string")) \


if __name__ == '__main__':
    experiment_name = os.environ["KUBEFLOW_EXPERIMENT_NAME"]
    pipeline_name = os.environ["KUBEFLOW_PIPELINE_NAME"]
    pipeline_version = os.environ["KUBEFLOW_PIPELINE_VERSION"]
    job_name = f"{pipeline_name}-{pipeline_version}"
    kubeflow_user = os.environ["KUBEFLOW_USER"]
    kubeflow_password = os.environ["KUBEFLOW_PASSWORD"]
    kubeflow_host = os.environ["KUBEFLOW_HOST"]
    kubeflow_namespace = os.environ["KUBEFLOW_NAMESPACE"]
    compiled_pipeline_file = "pipeline.zip"
    docker_image_name = os.environ["EXECUTOR_DOCKER_IMAGE"]
    docker_image_pull_policy = os.environ["EXECUTOR_DOCKER_IMAGE_PULL_POLICY"]

    # 1. build docker image
    subprocess.run(["docker", "build", "-t", docker_image_name, "."])
    # # Optionally: Push Docker image to remote registry

    # 2. compile the pipeline
    # mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE
    kfp.compiler.Compiler().compile(pipeline, compiled_pipeline_file)
    # Optionally: put it to some artifactory storage

    # Full SDK class reference: https://kubeflow-pipelines.readthedocs.io/en/stable/source/kfp.client.html#kfp.Client
    # Auth is required in order to access the KFP API from the outside of the cluster https://stackoverflow.com/a/72358528
    client = get_kfp_client(kubeflow_user, kubeflow_password, kubeflow_host, kubeflow_namespace)

    # 3. create or get experiment
    try:
        experiment = client.get_experiment(
            experiment_name=experiment_name,
            namespace=kubeflow_namespace
        )
    except ValueError as ex:
        experiment = client.create_experiment(
            name=experiment_name,
            description='',
            namespace=kubeflow_namespace
        )

    # 4. create or get the pipeline
    base_pipeline_id = client.get_pipeline_id(name=pipeline_name)

    if base_pipeline_id is None:
        pipeline = client.upload_pipeline(
            pipeline_package_path=compiled_pipeline_file,
            pipeline_name=pipeline_name,
            description=''
        )
    else:
        pipeline = client.upload_pipeline_version(
            pipeline_package_path=compiled_pipeline_file,
            pipeline_version_name=pipeline_version,
            pipeline_id=base_pipeline_id
        )

    # Optionally: run the pipeline
    run = client.run_pipeline(
        experiment_id=experiment.id,
        job_name=job_name,
        pipeline_id=base_pipeline_id or pipeline.id,
        version_id=pipeline.id if base_pipeline_id else None,
        enable_caching=False,
        params={}
    )

    # # Optionally: disable old recurring runs
    # recurring_runs = client.list_recurring_runs(experiment_id=experiment.id, sort_by='created_at desc')
    # for x in (recurring_runs.jobs if recurring_runs.jobs is not None else []):
    #     client.disable_job(job_id=x.id)

    # # Optionally: create new recurring run
    # job = client.create_recurring_run(
    #     experiment_id=experiment.id,
    #     job_name=job_name,
    #     cron_expression="0 1 * * *",
    #     max_concurrency=1,
    #     pipeline_id=base_pipeline_id or pipeline.id,
    #     version_id=pipeline.id if base_pipeline_id else None,
    #     enable_caching=False
    # )

    # # Optionally delete compiled pipeline file
    # os.remove(compiled_pipeline_file)
