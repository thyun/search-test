# API 참조 
#   https://docs.aws.amazon.com/opensearch-service/latest/developerguide/custom-packages.html#custom-packages-updating
#   https://docs.aws.amazon.com/opensearch-service/latest/developerguide/configuration-api.html#configuration-api-actions-listpackagesfordomain
#   https://boto3.amazonaws.com/v1/documentation/api/1.18.51/reference/services/opensearch.html
from requests_aws4auth import AWS4Auth
import boto3
import requests
import time
import sys

region = 'ap-northeast-2' # e.g. us-west-1
service = 'es'
src_domain_name = 'dev-search-es-710'
dest_domain_name = 'dev-search-es-250'
src_host = 'https://vpc-dev-search-es-710-oam5efg2l5nia7bqh2yvbneklu.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /
dest_host = 'https://vpc-dev-search-es-250-crdyurhlzxphmrjdfmtz7m23nu.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /

# Use assume-role
session = boto3.Session(profile_name="default")
sts = session.client("sts")
response = sts.assume_role(
    RoleArn="arn:aws:iam::175979101058:role/dev-srch-opensearch-access-role",
    RoleSessionName="es-access-session"
)
awsauth = AWS4Auth(response['Credentials']['AccessKeyId'], response['Credentials']['SecretAccessKey'], region, service, session_token=response['Credentials']['SessionToken'])

# Use local credential
#credentials = boto3.Session().get_credentials()
#awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def es_cat_indices(host, prefix=""):
  path = '_cat/indices'
  if len(prefix) > 0:
    path = f'_cat/indices/{prefix}*'
  
  url = host + path
  response = requests.get(url, auth=awsauth)
  return response.text

result = es_cat_indices(src_host)
print(result)

