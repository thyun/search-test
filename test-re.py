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
WORDS_SET = set(words.words())

#p = re.compile('([ㄱ-ㅎ가-힣0-9-_+?,:;][^a-zA-Z()\[\]<>]*)')
#p = re.compile('([a-zA-Z0-9-_+?,:;][^ㄱ-ㅎ가-힣()\[\]<>]*)')
subtitle_list = re.findall('[ㄱ-ㅎ가-힣0-9-_+?,:;][^a-zA-Z()\[\]<>]*|[a-zA-Z0-9-_+?,:;][^ㄱ-ㅎ가-힣()\[\]<>]*', "라 루나 (La Luna)")
for subtitle in subtitle_list:
    print(type(subtitle))
    print("===", subtitle, "===")


