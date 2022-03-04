# -*- coding: utf-8 -*-
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

API_HOST = "pri-admin.srch.skplanetx.com" # 상용
#API_HOST = "pri-admin.dev.srch.skplanetx.com" # 개발
API_PORT = 80
API_DICT_PATH = "/apis/v2/dictionary"

def call_api_list(keyword):
    conn = http.client.HTTPConnection(API_HOST, API_PORT)
    url = API_DICT_PATH + "/list"

    headers = {'Content-type': 'application/json'}
    body = {
  "chnl": "vcoloring",
  "requestData": {
    "channelId": 4,
    "type": 2,
    "keyword": keyword,
    "page": 0,
    "size": 10
  }
}
    json_data = json.dumps(body)
    conn.request("POST", url, json_data, headers)
    response = conn.getresponse()
    rsbody = response.read()
    jo = json.loads(rsbody)
    responseData = jo["responseData"]
    print("call_api_list(): keyword=", keyword, 
        "status=", response.status, "resCode1=", jo["resCode1"], "resCode2=", jo["resCode2"], "detailMsg=", jo["detailMsg"],
        "responseData.list=", responseData["list"])

    totalCnt = responseData["totalCnt"]
    if (totalCnt == 1):
        row = responseData["list"][0]
        return row["id"]
    return 0

def call_api_upsert(keyword, value, id):
    conn = http.client.HTTPConnection(API_HOST, API_PORT)
    url = API_DICT_PATH + "/upsert"

    headers = {'Content-type': 'application/json'}
    body = {
  "chnl": "vcoloring",
  "requestData": {
    "channelId": 4,
    "type": 2,
    "id": id,
    "keyword": keyword,
    "value": value,
    "delimiter": "",
    "useFlag": "1",
    "userId": "1001291"
  }
}
    json_data = json.dumps(body)
    conn.request("POST", url, json_data, headers)
    response = conn.getresponse()
    rsbody = response.read()
    jo = json.loads(rsbody)
    print("call_api_upsert(): keyword=", keyword, "value=", value, "id=", id,
        "status=", response.status, "resCode1=", jo["resCode1"], "resCode2=", jo["resCode2"], "detailMsg=", jo["detailMsg"])

def call_api_delete(id):
    conn = http.client.HTTPConnection(API_HOST, API_PORT)
    url = API_DICT_PATH + "/delete"

    headers = {'Content-type': 'application/json'}
    body = {
  "chnl": "vcoloring",
  "requestData": {
    "channelId": 4,
    "type": 2,
    "id": id,
    "userId": "1001291"
  }
}
    json_data = json.dumps(body)
    conn.request("POST", url, json_data, headers)
    response = conn.getresponse()
    rsbody = response.read()
    jo = json.loads(rsbody)
    print("call_api_delete(): keyword=", keyword, 
        "status=", response.status, "resCode1=", jo["resCode1"], "resCode2=", jo["resCode2"], "detailMsg=", jo["detailMsg"])

def insert_dict(keyword, value):
    call_api_upsert(keyword, value, 0)

def update_dict(keyword, value):
    id = call_api_list(keyword)
    if (id != 0):
        call_api_upsert(keyword, value, id)
    else:
        print("insert_dict(): id not found")

def upsert_dict(keyword, value):
    id = call_api_list(keyword)
    if (id != 0):
        call_api_upsert(keyword, value, id)
    else:
        call_api_upsert(keyword, value, 0)

def delete_dict(keyword):
    id = call_api_list(keyword)
    if (id != 0):
        call_api_delete(id)
    else:
        print("delete_dict(): id not found")

# 유사어 사전 생성 - 출력
def process_csv_synonym(file_path):
    noun_dict = { }
    print("process_csv_synonym() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            keyword = row['검색어']
            value = row['유의어']
            print(f"{keyword} => {value}")

# 유사어 사전 생성 - API 호출
# TODO 이미 존재하는 경우 아래 에러 출력 -> update 처리
# call_api_upsert(): keyword= Aminé value= Aminé,아미네,Amine id= 0 response.status= 200 resCode1= 999 resCode2= A001 detailMsg= 이미 등록된 검색어입니다.
def create_csv_synonym(file_path):
    noun_dict = { }
    print("create_csv_synonym() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            keyword = row['검색어']
            value = row['유사어']
            insert_dict(keyword.strip(), value)

# 유사어 사전 수정 - API 호출
# TODO id not found 에러 발생시 아래 에러 출력 - 0건 조회 경우, 2건 이상 조회 경우 반환된 list에서 keyword 값을 다시 찾아 봐야함
# insert_dict(): id not found
def update_csv_synonym(file_path):
    noun_dict = { }
    print("update_csv_synonym() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            keyword = row['검색어']
            value = row['유사어']
            update_dict(keyword.strip(), value)

### 테스트
#upsert_dict("aaa1", "aaa1")
#delete_dict("aaa1")

### Main
#process_csv_synonym("input/rmc-ict-synonym-20211206.csv")

#create_csv_synonym("input/rmc-ict-synonym-202202-create.csv")
#update_csv_synonym("input/rmc-ict-synonym-202202-create2.csv")
#update_csv_synonym("input/rmc-ict-synonym-202202-update.csv")

