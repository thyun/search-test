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
src_domain_name = 'prod-search-es-63-v1'
dest_domain_name = 'prod-search-es-68'
#src_host = 'https://search-dev-search-es-63-v2-dkl6ndeea7eens5fs2b2nlncbe.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /
#dest_host = 'https://search-dev-search-es-68-m3m4ba72w3vnzzx7isgdh74fre.ap-northeast-2.es.amazonaws.com/' # include https:// and trailing /
src_host = 'https://vpc-prod-search-es-63-v1-swr3qvtzjhbygz5lcaqufzfioy.ap-northeast-2.es.amazonaws.com/'
dest_host = 'https://vpc-prod-search-es-68-ms4p5ayzsizxydjnxlt4ph6utq.ap-northeast-2.es.amazonaws.com/'
query = '' # A test query to confirm the package has been successfully updated

service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

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

# Wait for the package to be updated
def wait_for_update(package_id, domain_name):
  opensearch = boto3.client('opensearch')
  response = opensearch.list_packages_for_domain(DomainName=domain_name)
  package_details = response['DomainPackageDetailsList']
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
def list_package(domain_name):
  opensearch = boto3.client('opensearch')
  print(domain_name)
  response = opensearch.list_packages_for_domain(
      DomainName=domain_name,
      MaxResults=100
  )

  packageIDList = []
  #print(response)
  for package in response["DomainPackageDetailsList"]:
      packageIDList.append(package["PackageID"])
  return packageIDList

# ****** Make sample search call to OpenSearch ******
def sample_search(query):
  path = '_search'
  params = {'q': query}
  url = dest_host + path
  response = requests.get(url, params=params, auth=awsauth)
  print('Searching for ' + '"' + query + '"')
  print(response.text)

#packageIDList = list_package(src_domain_name)
#print(packageIDList)

#associate_package('F53924013', dest_domain_name)
#wait_for_update('F53924013', dest_domain_name)

#dissociate_package('F108482429', dest_domain_name)

srcPackageIDList = list_package(src_domain_name)
destPackageIDList = list_package(dest_domain_name)
for packageID in srcPackageIDList:
  print(packageID)
  if (packageID in destPackageIDList):
    print(packageID, " is already associated")
    continue
  associate_package(packageID, dest_domain_name)
  wait_for_update(packageID, dest_domain_name)
