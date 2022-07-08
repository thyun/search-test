import boto3
import requests
from requests_aws4auth import AWS4Auth

dev_src_host = 'https://search-dev-search-es-68-m3m4ba72w3vnzzx7isgdh74fre.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /
dev_dest_host = 'https://vpc-dev-search-es-710-oam5efg2l5nia7bqh2yvbneklu.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /
prod_src_host = 'https://vpc-prod-search-es-68-ms4p5ayzsizxydjnxlt4ph6utq.ap-northeast-2.es.amazonaws.com/'
prod_dest_host = 'https://vpc-prod-search-es-710-3i5elzhiciqpwa2nv2ie5es3vu.ap-northeast-2.es.amazonaws.com/'
region = 'ap-northeast-2' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# Register repository - kibana에서 수행 불가 (권한 에러)
def register_repo_dev(host):
    path = '_snapshot/opensearch-backup' # the OpenSearch API endpoint
    url = host + path
    
    payload = {
      "type": "s3",
      "settings": {
        "bucket": "dev-srch-seoul-opensearch",
        "region": "ap-northeast-2",
        "role_arn": "arn:aws:iam::175979101058:role/dev-srch-snapshot-role"
      }
    }
    
    headers = {"Content-Type": "application/json"}
    
    r = requests.put(url, auth=awsauth, json=payload, headers=headers)
    
    print(r.status_code)
    print(r.text)

def register_repo_prod(host):
    path = '_snapshot/opensearch-backup' # the OpenSearch API endpoint
    url = host + path
    
    payload = {
      "type": "s3",
      "settings": {
        "bucket": "prod-srch-seoul-opensearch",
        "region": "ap-northeast-2",
        "role_arn": "arn:aws:iam::456350226269:role/prod-srch-snapshot-role"
      }
    }
    
    headers = {"Content-Type": "application/json"}
    
    r = requests.put(url, auth=awsauth, json=payload, headers=headers)
    
    print(r.status_code)
    print(r.text)

# Take snapshot - kibana에서 수행 가능
def take_snapshot():
    path = '_snapshot/opensearch-backup/snapshot-20211222'
    url = host + path
    
    r = requests.put(url, auth=awsauth)
    
    print(r.text)
   
# Delete index - kibana에서 수행 가능
def del_index(): 
    path = 'my-index'
    url = host + path
    
    r = requests.delete(url, auth=awsauth)
    
    print(r.text)

# Restore snapshot (all indices except Dashboards and fine-grained access control) - kibana에서 수행 가능
def restore_snapshot():
    path = '_snapshot/opensearch-backup/snapshot-20211222/_restore'
    url = host + path
    
    payload = {
      "indices": "-.kibana*,-auto_complete",
      #"indices": "-.kibana*,-test-*",
      #"indices": "-.kibana*,-.opendistro_security",
      "include_global_state": False
    }
    
    headers = {"Content-Type": "application/json"}
    
    r = requests.post(url, auth=awsauth, json=payload, headers=headers)
    
    print(r.text)

# Restore snapshot (one index) - kibana에서 수행 가능
def restore_snapshot_index(): 
    path = '_snapshot/opensearch-backup/snapshot-20211222/_restore?wait_for_completion=true'
    url = host + path
   
    payload = {"indices": "vcoloring_keyword_rmc_202112220600"}
   
    headers = {"Content-Type": "application/json"}
   
    r = requests.post(url, auth=awsauth, json=payload, headers=headers)
   
    print(r.text)

#register_repo_dev(dev_dest_host)
register_repo_prod(prod_dest_host)
#take_snapshot()
#restore_snapshot()
#restore_snapshot_index()

