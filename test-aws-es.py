from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from requests_aws4auth import AWS4Auth
import boto3
import json
from datetime import datetime

# Check Connection

host = 'search-dev-search-es-63-v2-dkl6ndeea7eens5fs2b2nlncbe.ap-northeast-2.es.amazonaws.com'
region = 'ap-northeast-2'

service = 'es'
session = boto3.Session()
credentials = session.get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es', session_token=credentials.token)
# awsauth = AWS4Auth(access_key, secret_key, region, service)
print(credentials.access_key)

es = Elasticsearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = awsauth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    timeout=30, max_retries=10, retry_on_timeout=True
)

es.indices.create(index="test-aaa")

print(es.info())
