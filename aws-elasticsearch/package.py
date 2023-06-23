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
dest_host = 'https://vpc-dev-search-es-710-oam5efg2l5nia7bqh2yvbneklu.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /
#src_domain_name = 'prod-search-es-710'
#dest_domain_name = 'prod-search-es-250'
#src_host = 'https://vpc-prod-search-es-68-ms4p5ayzsizxydjnxlt4ph6utq.ap-northeast-2.es.amazonaws.com/'
#dest_host = 'https://vpc-prod-search-es-710-3i5elzhiciqpwa2nv2ie5es3vu.ap-northeast-2.es.amazonaws.com/'
query = '' # A test query to confirm the package has been successfully updated

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

# ****** json key exist ******
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

# ****** Update the package in OpenSearch Service *******
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

# ****** Associate/Dissociate the package to the domain
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

# Wait for the package to be updated
def wait_for_update(package_id, domain_name):
  opensearch = boto3.client('opensearch')
  response = opensearch.list_packages_for_domain(DomainName=domain_name)
  package_details = response['DomainPackageDetailsList']

  # associate -> wait for ACTIVE, dissociate -> wait for no package in package_details
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
        wait_for_update(package_id, domain_name)

# ****** List package for domain ******
def list_package(domain_name, prefix=""):
  print(f"List package: {domain_name} prefix={prefix}")
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

# Sync package
def sync_package(src_domain_name, dest_domain_name, prefix=""):
  print("Sync package:")
  srcPackageIDList = list_package(src_domain_name, prefix)
  destPackageIDList = list_package(dest_domain_name)
  for packageID in srcPackageIDList:
    print(f"Sync {packageID}")
    if (packageID in destPackageIDList):
      print(packageID, " is already associated")
      continue
    associate_package(packageID, dest_domain_name)
    wait_for_update(packageID, dest_domain_name)

# Clean package
def clean_package(domain_name, prefix=""):
  print("Clean package:")
  packageIDList = list_package(domain_name, prefix)
  for packageID in packageIDList:
    dissociate_package(packageID, domain_name)
    wait_for_update(packageID, dest_domain_name)

# ****** ES ******
# words = ['green', 'open', 'vcoloring_ac_request_202211071411', '0cE_7eL7RmqkOjr-0OtS8A', '3', '0', '369', '0', '50.6kb', '50.6kb']
def find_indices_package(prefix=""):
  text = es_cat_indices(prefix)
  lines = text.splitlines()
  for line in lines:
    words = line.split() 
    index = words[2]
    response = es_get_index(index)
    jo = response.json()

    nested_keys = [index, "settings", "index", "analysis", "tokenizer", "seunjeon", "user_dict_path"]
    user_dict_path = get_nested_value(jo, nested_keys)
    nested_keys = [index, "settings", "index", "analysis", "filter", "synonym_filter", "synonyms_path"]
    synonyms_path = get_nested_value(jo, nested_keys)
    if user_dict_path is not None or synonyms_path is not None:
      print(f"index={index} user_dict_path={user_dict_path} synonyms_path={synonyms_path}")

def find_package_indices(packageID):
  text = es_cat_indices()
  lines = text.splitlines()
  for line in lines:
    words = line.split() 
    index = words[2]
    response = es_get_index(index)
    jo = response.json()

    nested_keys = [index, "settings", "index", "analysis", "tokenizer", "seunjeon", "user_dict_path"]
    user_dict_path = get_nested_value(jo, nested_keys)
    nested_keys = [index, "settings", "index", "analysis", "filter", "synonym_filter", "synonyms_path"]
    synonyms_path = get_nested_value(jo, nested_keys)
    if user_dict_path is not None or synonyms_path is not None:
      if user_dict_path.endswith(packageID) or synonyms_path.endswith(packageID):
        print(f"index={index} user_dict_path={user_dict_path} synonyms_path={synonyms_path}")

def es_cat_indices(prefix=""):
  path = '_cat/indices'
  if len(prefix) > 0:
    path = f'_cat/indices/{prefix}*'
  
  url = dest_host + path
  response = requests.get(url, auth=awsauth)
  return response.text

def es_get_search(query):
  path = '_search'
  params = {'q': query}
  url = dest_host + path
  response = requests.get(url, params=params, auth=awsauth)
  print('Searching for ' + '"' + query + '"')
  print(response.text)
  return response

def es_get_index(index):
  path = f'{index}'
  #params = {'q': query}
  url = dest_host + path
  response = requests.get(url, auth=awsauth)
  #print(response.text)
  return response

# Test
#associate_package('F192314680', dest_domain_name)
#wait_for_update('F192314680', dest_domain_name)
#dissociate_package('F192314680', dest_domain_name)
#wait_for_update('F192314680', dest_domain_name)

#packageIDList = list_package(src_domain_name, "vcoloring")
#sync_package(src_domain_name, dest_domain_name, "vcoloring")
#clean_package(dest_domain_name, "vcoloring")

find_indices_package("vcoloring")
#find_package_indices("F132754625")

