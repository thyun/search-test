# API 참조 
#   https://docs.aws.amazon.com/opensearch-service/latest/developerguide/custom-packages.html#custom-packages-updating
#   https://docs.aws.amazon.com/opensearch-service/latest/developerguide/configuration-api.html#configuration-api-actions-listpackagesfordomain
#   https://boto3.amazonaws.com/v1/documentation/api/1.18.51/reference/services/opensearch.html
from requests_aws4auth import AWS4Auth
import boto3
import requests
import time
import json
import sys

region = 'ap-northeast-2' # e.g. us-west-1
file_name = '' # The path to the file to upload
bucket_name = '' # The name of the S3 bucket to upload to
s3_key = '' # The name of the S3 key (file name) to upload to
package_id = 'F96034076' # The unique identifier of the OpenSearch package to update
src_domain_name = 'dev-search-es-710'
dest_domain_name = 'dev-search-es-250'
src_host = 'https://vpc-dev-search-es-710-oam5efg2l5nia7bqh2yvbneklu.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /
dest_host = 'https://vpc-dev-search-es-250-crdyurhlzxphmrjdfmtz7m23nu.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /
#src_domain_name = 'prod-search-es-710'
#dest_domain_name = 'prod-search-es-250'
#src_host = 'https://vpc-prod-search-es-68-ms4p5ayzsizxydjnxlt4ph6utq.ap-northeast-2.es.amazonaws.com/'
#dest_host = 'https://vpc-prod-search-es-710-3i5elzhiciqpwa2nv2ie5es3vu.ap-northeast-2.es.amazonaws.com/'
query = '' # A test query to confirm the package has been successfully updated

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

DOMAIN_CONFIGS = [
  { "domain_name": src_domain_name, "domain_host": src_host },
  { "domain_name": dest_domain_name, "domain_host": dest_host }
]

# ****** Get config ******
def get_domain_name_ep(domain_name):
  for domain_config in DOMAIN_CONFIGS:
    if domain_name == domain_config["domain_name"]:
      return domain_config["domain_host"]

# ****** Get json nested key ******
def check_nested_value(json_obj, keys):
    if isinstance(json_obj, dict):
        key = keys[0]
        if key in json_obj:
            if len(keys) == 1:
                return True
            return check_nested_value(json_obj[key], keys[1:])
    return False

def get_nested_value(json_obj, keys):
    if isinstance(json_obj, dict):
        key = keys[0]
        if key in json_obj:
            if len(keys) == 1:
                return json_obj[key]
            return get_nested_value(json_obj[key], keys[1:])
    return None

# Example JSON object as a string
json_string = '''
{
    "name": "John",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "New York",
        "country": "USA"
    }
}
'''

# Check if nested key-value pair exists
def test_nested_json():
  json_object = json.loads(json_string)
  nested_keys = ["address", "city"]
  if check_nested_value(json_object, nested_keys):
      print("Nested key-value pair exists!")
  else:
      print("Nested key-value pair does not exist.")

# ****** Upload file to S3 ******
def upload_to_s3(file_name, bucket_name, s3_key):
  s3 = boto3.client('s3')
  try:
    s3.upload_file(file_name, bucket_name, s3_key)
    print('Upload successful')
    return True
  except FileNotFoundError:
    sys.exit('File not found. Make sure you specified the correct file path.')

# ****** OpenSearch package *******
def update_package(package_id, bucket_name, s3_key):
  opensearch = boto3.client('opensearch')
  print(package_id, bucket_name, s3_key)
  response = opensearch.update_package(
      PackageID= package_id,
      PackageSource={
          'S3BucketName': bucket_name,
          'S3Key': s3_key
      }
  )
  print(response)

# Associate/Dissociate the package to the domain
def associate_package(package_id, domain_name):
  opensearch = boto3.client('opensearch')
  response = opensearch.associate_package(PackageID=package_id, DomainName=domain_name)
  print(response)
  print('Associating...')

def dissociate_package(package_id, domain_name):
  opensearch = boto3.client('opensearch')
  response = opensearch.dissociate_package(PackageID=package_id, DomainName=domain_name)
  print(response)
  print('Dissociating...')

def associate_package_complete(package_id, domain_name):
  associate_package(package_id, domain_name)
  wait_for_associate(package_id, domain_name)

def dissociate_package_complete(package_id, domain_name):
  dissociate_package(package_id, domain_name)
  wait_for_dissociate(package_id, domain_name)

#wait_for_associate('F180796364', dest_domain_name)
# Wait for the package to be updated
def wait_for_associate(package_id, domain_name):
  opensearch = boto3.client('opensearch')
  response = opensearch.list_packages_for_domain(DomainName=domain_name)
  package_details = response['DomainPackageDetailsList']

  # associate -> wait for ACTIVE
  for package in package_details:
    if package['PackageID'] == package_id:
      status = package['DomainPackageStatus']
      if status == 'ACTIVE':
        print('Association successful.')
        return
      elif status == 'ASSOCIATION_FAILED':
        sys.exit('Association failed. Please try again.')
      else:
        time.sleep(10) # Wait 10 seconds before rechecking the status
        wait_for_associate(package_id, domain_name)

def wait_for_dissociate(package_id, domain_name):
  opensearch = boto3.client('opensearch')
  response = opensearch.list_packages_for_domain(DomainName=domain_name)
  package_details = response['DomainPackageDetailsList']

  # dissociate -> wait for no package in package_details
  for package in package_details:
    if package['PackageID'] == package_id:
      status = package['DomainPackageStatus']
      time.sleep(10) # Wait 10 seconds before rechecking the status
      wait_for_dissociate(package_id, domain_name)

# List package for domain
def list_packages_for_domain(domain_name, prefix=""):
  print(f"list_packages_for_domain: {domain_name} prefix={prefix}")
  opensearch = boto3.client('opensearch')
  response = opensearch.list_packages_for_domain(
      DomainName=domain_name,
      MaxResults=100
  )

  packageIDList = []
  #print(response)
  for package in response["DomainPackageDetailsList"]:
    if len(prefix) == 0:
      print(package["PackageID"], " ", package["PackageName"])
      packageIDList.append(package["PackageID"])
    elif package["PackageName"].startswith(prefix): 
      print(package["PackageID"], " ", package["PackageName"])
      packageIDList.append(package["PackageID"])
  return packageIDList

def list_domains_for_package(packageID):
  opensearch = boto3.client('opensearch')
  response = opensearch.list_domains_for_package(
    PackageID=packageID,
    MaxResults=100
  )
  results = []
  for domainPackageDetail in response["DomainPackageDetailsList"]:
    domain_name = domainPackageDetail["DomainName"]
    results.append(domain_name)
  return results

# List all packages
def describe_packages():
  opensearch = boto3.client('opensearch')
  response = opensearch.describe_packages(
    MaxResults=100
  )
  return(response)

def delete_package(packageID):
  opensearch = boto3.client('opensearch')
  response = opensearch.delete_package(
    PackageID=packageID
  )

def list_unused_packages():
  response = describe_packages()

  for packageDetail in response["PackageDetailsList"]:
    packageID = packageDetail["PackageID"]
    results = list_domains_for_package(packageID)
    if len(results) == 0:
      print(f"packageID={packageID} used=false");
      #delete_package(packageID)

# Sync package list
def sync_package_list(src_domain_name, dest_domain_name, prefix=""):
  print("Sync package:")
  srcPackageIDList = list_packages_for_domain(src_domain_name, prefix)
  destPackageIDList = list_packages_for_domain(dest_domain_name)
  for packageID in srcPackageIDList:
    print(f"Sync {packageID}")
    if (packageID in destPackageIDList):
      print(packageID, " is already associated")
      continue
    associate_package_complete(packageID, dest_domain_name)

# Dissociate package list
def dissociate_package_list(domain_name, prefix=""):
  packageIDList = list_packages_for_domain(domain_name, prefix)
  for packageID in packageIDList:
    dissociate_package_complete(packageID, domain_name)

# words = ['green', 'open', 'vcoloring_ac_request_202211071411', '0cE_7eL7RmqkOjr-0OtS8A', '3', '0', '369', '0', '50.6kb', '50.6kb']
def find_indices_package(domain_name, prefix=""):
  host = get_domain_name_ep(domain_name)
  print(f"find_indices_package: host={host}")
  text = es_cat_indices(host, prefix)
  lines = text.splitlines()
  for line in lines:
    words = line.split() 
    index = words[2]
    response = es_get_index(host, index)
    #print(response.text)
    jo = response.json()

    nested_keys = [index, "settings", "index", "analysis", "tokenizer", "seunjeon", "user_dict_path"]
    user_dict_path = get_nested_value(jo, nested_keys)
    nested_keys = [index, "settings", "index", "analysis", "filter", "synonym_filter", "synonyms_path"]
    synonyms_path = get_nested_value(jo, nested_keys)
    if user_dict_path is not None or synonyms_path is not None:
      print(f"index={index} user_dict_path={user_dict_path} synonyms_path={synonyms_path}")

def find_indices_package2(domain_name, prefix=""):
  host = get_domain_name_ep(domain_name)
  print(f"find_indices_package: host={host}")
  text = es_cat_indices(host, prefix)
  print(text)
  lines = text.splitlines()
  results = []
  for line in lines:
    words = line.split() 
    index = words[2]
    response = es_get_index(host, index)
    #print(response.text)
    jo = response.json()

    nested_keys = [index, "settings", "index", "analysis", "tokenizer", "seunjeon", "user_dict_path"]
    user_dict_path = get_nested_value(jo, nested_keys)
    nested_keys = [index, "settings", "index", "analysis", "filter", "synonym_filter", "synonyms_path"]
    synonyms_path = get_nested_value(jo, nested_keys)
    if user_dict_path is not None or synonyms_path is not None:
      #print(f"index={index} user_dict_path={user_dict_path} synonyms_path={synonyms_path}")
      results.append({"index": index, "user_dict_path": user_dict_path, "synonyms_path": synonyms_path })
  return results

def find_package_indices(domain_name, packageID):
  host = get_domain_name_ep(domain_name)
  text = es_cat_indices(host)
  print(text)
  lines = text.splitlines()
  results = []
  for line in lines:
    words = line.split() 
    index = words[2]
    response = es_get_index(host, index)
    #print(index)
    #print(response.text)
    jo = response.json()

    nested_keys = [index, "settings", "index", "analysis", "tokenizer", "seunjeon", "user_dict_path"]
    user_dict_path = get_nested_value(jo, nested_keys)
    nested_keys = [index, "settings", "index", "analysis", "filter", "synonym_filter", "synonyms_path"]
    synonyms_path = get_nested_value(jo, nested_keys)
    if user_dict_path is not None and user_dict_path.endswith(packageID):
        print(f"index={index} user_dict_path={user_dict_path}")
        results.append(index)
    elif synonyms_path is not None and synonyms_path.endswith(packageID):
        print(f"index={index} synonyms_path={synonyms_path}")
        results.append(index)
  return results

# index format: {'index': 'ocb_keyword_homeshopping52_v2_202306231612', 'user_dict_path': 'analyzers/F180796364', 'synonyms_path': 'analyzers/F232408093'}
def lookup_indices(indices, packageID):
  for index in indices:
    user_dict_path = index["user_dict_path"]
    synonyms_path = index["synonyms_path"]
    if user_dict_path is not None and user_dict_path.endswith(packageID):
      return index
    if synonyms_path is not None and synonyms_path.endswith(packageID):
      return index
  return None

def clean_domain_package(domain_name):
  indices = find_indices_package2(domain_name)
  packages = list_packages_for_domain(domain_name)
  print(indices)
  print(packages)
  for packageID in packages:
    index = lookup_indices(indices, packageID)
    if index is not None:
      print(f"packageID={packageID} used=true {index}")
    else:
      print(f"packageID={packageID} used=false")
      dissociate_package_complete(packageID, domain_name)

# ****** OpenSearch index *******
def es_cat_indices(host, prefix=""):
  path = '_cat/indices'
  if len(prefix) > 0:
    path = f'_cat/indices/{prefix}*'
  
  url = host + path
  response = requests.get(url, auth=awsauth)
  return response.text

def es_get_search(host, query):
  path = '_search'
  params = {'q': query}
  url = host + path
  response = requests.get(url, params=params, auth=awsauth)
  print('Searching for ' + '"' + query + '"')
  print(response.text)
  return response

def es_get_index(host, index):
  path = f'{index}'
  #params = {'q': query}
  url = host + path
  response = requests.get(url, auth=awsauth)
  #print(response.text)
  return response

# 테스트 - Associate/dissociate package
# index=ocb_keyword_homeshopping52_v2_202306231612 user_dict_path=analyzers/F180796364 synonyms_path=analyzers/F232408093
#dissociate_package_complete('F180796364', dest_domain_name)
#dissociate_package_complete('F232408093', dest_domain_name)

# 테스트 - List package for domain
packageIDList = list_packages_for_domain(src_domain_name)
#packageIDList = list_packages_for_domain(src_domain_name, "ocb-")

# 테스트 - Sync package
# TODO delete_index_list - 현재 Kibana에서 처리
#sync_package_list(src_domain_name, dest_domain_name, "vcoloring-")
#delete_index_list(src_domain_name, "vcoloring_")
#dissociate_package_list(src_domain_name, "vcoloring-")

# 테스트 - index - package 관계 찾기
# TODO aws account의 ESHttpGet 권한 없음
# {"Message":"User: arn:aws:sts::175979101058:assumed-role/AWSReservedSSO_OA-developer-common_a041ac6963b123ac/th.yun@skplanet.com is not authorized to perform: es:ESHttpGet with an explicit deny in a service control policy"}
#indices = find_indices_package2(src_domain_name, "ocb_")
#indices = find_package_indices(src_domain_name, "F98879945")

# 테스트 - Clean packages for domain, List unused packages
#clean_domain_package(src_domain_name)
#clean_domain_package(dest_domain_name)
#list_unused_packages()

#sync_package_list(src_domain_name, dest_domain_name, "syrup-")

