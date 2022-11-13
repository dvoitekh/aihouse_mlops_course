import kfp
import requests

from kubernetes.client.models import V1EnvVar, V1EnvVarSource, V1SecretKeySelector


def generate_env_secret_variable(name, secret_name, secret_key):
    return V1EnvVar(
        name=name,
        value_from=V1EnvVarSource(
            secret_key_ref=V1SecretKeySelector(
                name=secret_name,
                key=secret_key
            )
        )
    )


def get_kubeflow_session_cookie(username, password, host):
    session = requests.Session()
    response = session.get(host)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"login": username, "password": password}

    session.post(response.url, headers=headers, data=data)
    return session.cookies.get_dict()["authservice_session"]


def get_kfp_client(username, password, host, namespace):
    session_cookie = get_kubeflow_session_cookie(username, password, host)
    return kfp.Client(
        host=f"{host}/pipeline",
        namespace=namespace,
        cookies=f"authservice_session={session_cookie}"
    )
