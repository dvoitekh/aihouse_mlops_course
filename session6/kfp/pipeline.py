import kfp
import os
import subprocess
import kfp.dsl as dsl
from dotenv import load_dotenv

from kfp.components import create_component_from_func

from src.utils import get_kfp_client, generate_env_secret_variable

from components.notification import notification
from components.dataset_generation import dataset_generation
from components.eda import eda
from components.training import training
from components.evaluation import evaluation


@dsl.pipeline(name='House Pricing Pipeline', description='')
def pipeline(validation_dataset_fraction: float = 0.1, random_seed: int = 1):
    base_image = os.environ["EXECUTOR_DOCKER_IMAGE"]
    docker_image_pull_policy = os.environ["EXECUTOR_DOCKER_IMAGE_PULL_POLICY"]

    # Persistent volume (deprecated) might be helpful in case you need to share multiple heavy files between components:
    # vop = dsl.VolumeOp(
    #     name="pipeline-pvc", resource_name="data-volume", modes=dsl.VOLUME_MODE_RWO, size="1Gi"
    # )
    # .add_pvolumes({'/tmp': vop.volume}) \

    notification_op = create_component_from_func(notification,
                                                 base_image=base_image,
                                                 packages_to_install=[],
                                                 output_component_file='specs/notification.yaml')

    dataset_generation_op = create_component_from_func(dataset_generation,
                                                       base_image=base_image,
                                                       packages_to_install=['feast[aws,redis]==0.26.0'],
                                                       output_component_file='specs/dataset_generation.yaml')

    eda_op = create_component_from_func(eda,
                                        base_image=base_image,
                                        packages_to_install=['pandas-profiling==3.4.0'],
                                        output_component_file='specs/eda.yaml')

    training_op = create_component_from_func(training,
                                             base_image=base_image,
                                             packages_to_install=[],
                                             output_component_file='specs/training.yaml')

    evaluation_op = create_component_from_func(evaluation,
                                               base_image=base_image,
                                               packages_to_install=[],
                                               output_component_file='specs/evaluation.yaml')

    # We can also load components from existing yaml definitions:
    # kubeflow.org/docs/components/pipelines/v1/sdk/component-development/#using-your-component-in-a-pipeline
    # from kfp.components import load_component_from_file
    # training_op = load_component_from_file('components/training/component.yaml')

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
        dataset_generation_step = dataset_generation_op(validation_dataset_fraction, random_seed) \
                                                         .add_resource_request('memory', '500Mi') \
                                                         .add_resource_request('cpu', '500m') \
                                                         .add_resource_limit('memory', '500Mi') \
                                                         .add_resource_limit('cpu', '500m') \
                                                         .set_image_pull_policy(docker_image_pull_policy)

        train_eda_step = eda_op(dataset_generation_step.outputs['train_dataset']).add_resource_request('memory', '500Mi') \
                                                                                 .add_resource_request('cpu', '500m') \
                                                                                 .add_resource_limit('memory', '1000Mi') \
                                                                                 .add_resource_limit('cpu', '1000m')

        val_eda_step = eda_op(dataset_generation_step.outputs['val_dataset']).add_resource_request('memory', '500Mi') \
                                                                             .add_resource_request('cpu', '500m') \
                                                                             .add_resource_limit('memory', '1000Mi') \
                                                                             .add_resource_limit('cpu', '1000m')

        training_step = training_op(dataset_generation_step.outputs['train_dataset']).add_resource_request('memory', '500Mi') \
                                                                                     .add_resource_request('cpu', '500m') \
                                                                                     .add_resource_limit('memory', '1000Mi') \
                                                                                     .add_resource_limit('cpu', '1000m') \
                                                                                     .set_image_pull_policy(docker_image_pull_policy)

        evaluation_step = evaluation_op(training_step.outputs['model'],
                                        training_step.outputs['preprocessor'],
                                        dataset_generation_step.outputs['val_dataset']).add_resource_request('memory', '500Mi') \
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
    load_dotenv()

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
    # Optionally: Push Docker image to remote registry
    if os.environ.get("PUSH_DOCKER_IMAGE") == "true":
        subprocess.run(["docker", "push", docker_image_name])

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
        params={
            'validation_dataset_fraction': 0.2,
            'random_seed': 42
        }
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
