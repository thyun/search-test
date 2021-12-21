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

API_HOST = "pri-api.dev.srch.skplanetx.com"
API_PORT = 80
API_PATH = "/api/common/analyze/tokenizer"

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

def process_csv_synonym_keyword(file_path):
    noun_dict = { }
    print("process_csv_synonym_keyword() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            keyword = row['검색어']
            value = row['유의어']
            if ("," in keyword):
                print(f"{keyword} => {value}")

process_csv_synonym_keyword("rmc-ict-synonym-20211206.csv")

