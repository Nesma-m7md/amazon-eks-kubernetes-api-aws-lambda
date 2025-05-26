import base64
import logging
from botocore.signers import RequestSigner
from kubernetes import client, config
from kubeconfig import get_config
import logging, logging.handlers

def lambda_handler(event, context):
    "Lambda handler"
    try:
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Get Kubeconfig
        kubeconfig=get_config()
        config.load_kube_config_from_dict(config_dict=kubeconfig)
        v1_api = client.CoreV1Api() # api_client
        pods = v1_api.list_namespaced_pod("default")
        for pod in pods.items:
            print(f"{pod.metadata.namespace}: {pod.metadata.name} - {pod.status.phase}")

    # send pipeline response failed if lambda logs has error
    except Exception as error:
        logger.exception(error)