import base64
import os
import re
import boto3
import kubernetes
from botocore.signers import RequestSigner
from kubernetes import client, config

cluster_cache = {}
STS_TOKEN_EXPIRES_IN = 120

def get_config():
    cluster_name=os.environ['cluster_name']
    session = boto3.session.Session(region_name='eu-west-1')
    sts = session.client('sts',region_name='eu-west-1')
    service_id = sts.meta.service_model.service_id
    cluster_name = cluster_name
    eks = boto3.client('eks',region_name='eu-west-1')

    def get_cluster_info():
        "Retrieve cluster endpoint and certificate"
        cluster_info = eks.describe_cluster(name=cluster_name)
        endpoint = cluster_info['cluster']['endpoint']
        cert_authority = cluster_info['cluster']['certificateAuthority']['data']
        cluster_info = {
            "endpoint" : endpoint,
            "ca" : cert_authority
        }
        return cluster_info

    def get_bearer_token():
        "Create authentication token"
        signer = RequestSigner(
            service_id,
            session.region_name,
            'sts',
            'v4',
            session.get_credentials(),
            session.events
        )

        params = {
            'method': 'GET',
            'url': 'https://sts.{}.amazonaws.com/'
            '?Action=GetCallerIdentity&Version=2011-06-15'.format(session.region_name),
            'body': {},
            'headers': {
                'x-k8s-aws-id': cluster_name
            },
            'context': {}
        }

        signed_url = signer.generate_presigned_url(
            params,
            region_name=session.region_name,
            expires_in=STS_TOKEN_EXPIRES_IN,
            operation_name=''
        )
        base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')

        # remove any base64 encoding padding:
        return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)

    if cluster_name in cluster_cache:
        cluster = cluster_cache[cluster_name]
    else:
        # not present in cache retrieve cluster info from EKS service
        cluster = get_cluster_info()
        # store in cache for execution environment resuse
        cluster_cache[cluster_name] = cluster

    kubeconfig = {
            'apiVersion': 'v1',
            'clusters': [{
            'name': 'cluster1',
            'cluster': {
                'certificate-authority-data': cluster["ca"],
                'server': cluster["endpoint"]}
            }],
            'contexts': [{'name': 'context1', 'context': {'cluster': 'cluster1', "user": "user1"}}],
            'current-context': 'context1',
            'kind': 'Config',
            'preferences': {},
            'users': [{'name': 'user1', "user" : {'token': get_bearer_token()}}]
    }
    return kubeconfig