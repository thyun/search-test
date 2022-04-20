# title명으로 유사어 사전 생성
# artist명으로 사용자 사전 생성
import json
import re
import http.client # python3에서 httplib -> http.client 로 변경됨. class는 동일
from urllib import parse
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
import csv
from nltk.corpus import words
# import nltk
# nltk.download('words')

API_HOST = "pri-api.dev.srch.skplanetx.com"
API_PORT = 80
API_PATH = "/api/common/validate"

def api_validate(keywords):
    conn = http.client.HTTPConnection(API_HOST, API_PORT)
    query = [('channel', 'vcoloring'), ('keywords', keywords)]
    url = API_PATH + "?" + parse.urlencode(query)
    conn.request("GET", url)
    response = conn.getresponse()
    rsbody = response.read()
    #print response.status, response.reason

    # Parse response
    rsdoc = json.loads(rsbody)
    error_count = rsdoc["error_count"]
    return error_count

def process_csv(file_path):
    total = 0
    print("process_csv() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file, delimiter='|')
        for row in reader:
            keywords = row['value']
            total += 1
            error_count = api_validate(keywords)
            if (error_count > 0):
                print(f"keywords={keywords}")



### main
process_csv("value.csv")
#error_count = api_validate("no,노")
#print(f"error_count={error_count}")

