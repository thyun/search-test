# 사업팀 생성 사전 데이터 처리
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

API_HOST = "pri-admin.dev.srch.skplanetx.com"
API_PORT = 80
API_UPSERT_PATH = "/apis/v2/dictionary/upsert"

def call_api(keyword, value):
    conn = http.client.HTTPConnection(API_HOST, API_PORT)
    url = API_UPSERT_PATH

    headers = {'Content-type': 'application/json'}
    body = {
  "chnl": "vcoloring",
  "requestData": {
    "channelId": 4,
    "type": 2,
    "id": 0,
    "keyword": keyword,
    "value": value,
    "delimiter": "",
    "useFlag": "1",
    "userId": "1001291"
  }
}
    json_data = json.dumps(body)
    print("json_data=", json_data)

    conn.request("POST", url, json_data, headers)
    response = conn.getresponse()
    rsbody = response.read()
    print(response.status, rsbody)

def process_csv_userdict(file_path):
    noun_dict = { }
    total = 0
    print("process_csv() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            title = row['title']
            if (len(title) > 0):
                cnoun_list = process_title(title)
                for cnoun in cnoun_list:
                    noun_dict[cnoun] = cnoun
            total += 1
#            if (total >= 100):
#               break
    return noun_dict

def process_csv_synonym(file_path):
    noun_dict = { }
    print("process_csv_synonym() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            keyword = row['검색어']
            value = row['유의어']
            print(f"{keyword} => {value}")

def process_csv_synonym2(file_path):
    noun_dict = { }
    print("process_csv_synonym_keyword() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            keyword = row['검색어']
            value = row['유사어']
            print(f"{keyword} => {value}")

#process_csv_synonym("rmc-ict-synonym-20211206.csv")
#process_csv_synonym2("rmc-ict-synonym-create-202202.csv")
call_api("aaa1", "aaa1")

