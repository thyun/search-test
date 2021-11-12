import json
import re
import http.client # python3에서 httplib -> http.client 로 변경됨. class는 동일
from urllib import parse
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
import csv

API_HOST = "pri-api.dev.srch.skplanetx.com"
API_PORT = 80
API_PATH = "/api/common/analyze/tokenizer"

def get_doc_from_line(line):
    doc = json.loads(line)
    return doc

def call_api(keyword):
    conn = http.client.HTTPConnection(API_HOST, API_PORT)
    query = [('channel', 'vcoloring'), ('keyword', keyword)]
    url = API_PATH + "?" + parse.urlencode(query)
    conn.request("GET", url)
    response = conn.getresponse()
    rsbody = response.read()
    #print response.status, response.reason

    # Parse response
    rsdoc = json.loads(rsbody)
    token_list = []
    for token in rsdoc["tokens"]:
        token_list.append(token["token"])
    return token_list

def is_english_only(s):
    p = re.compile('[a-zA-Z-_\.\\s]+$') # a-z A-Z - _ . blank
    m = p.match(s)
    if m:
        return True
    return False

def process_title(title):
    noun_list = [ ]
    print(f"title={title}")
    p = re.compile('[a-zA-Zㄱ-ㅎ가-힣0-9][^()]*[a-zA-Zㄱ-ㅎ가-힣0-9]')
    subtitle_list = p.findall(title)
    print(f"subtitle_list={subtitle_list}")
    for subtitle in subtitle_list:
        noun_list.extend(process_subtitle(subtitle))
    return noun_list

def process_subtitle(subtitle):
    noun_list = [ ]
    nsubtitle, n = re.subn("\\s+", "", subtitle)
    if (is_english_only(subtitle)):
        return noun_list
    if (subtitle == nsubtitle):
        return noun_list

    token_list = call_api(subtitle)
    ntoken_list = call_api(nsubtitle)
    print(f"subtitle={subtitle} token_list={token_list}")
    print(f"nsubtitle={nsubtitle} ntoken_list={ntoken_list}")
    sorted_token_list = sorted(token_list)
    sorted_ntoken_list = sorted(ntoken_list)
    if (sorted_token_list != sorted_ntoken_list):
        cnoun, n = re.subn("\\s+", "+", subtitle)
        noun_list.append(cnoun)
    return noun_list

RE_SPECIAL = "[\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"]"
#RE_SPECIAL = "[^0-9a-zA-Z]"
def process_artist(artist):
    nartist, n = re.subn(RE_SPECIAL, " ", artist)
    nartist, n = re.subn("\\s+", " ", nartist)
    return nartist.split()

def process_csv_title(file_path):
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
#                break
    return noun_dict

def process_csv_artist(file_path):
    noun_dict = { }
    print("process_csv_artist() start: {} {}".format(file_path, datetime.today()))
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            artist = row['artist']
            if (len(artist) > 0):
                noun_list = process_artist(artist)
                print(artist, "=>", noun_list)

            for noun in noun_list:
                if (len(noun) > 1 and not noun in noun_dict):
                    noun_dict[noun] = noun
                else:
                    print("Duplicate or length=1", noun)
    return noun_dict

def process_json(file_path):
    print("process_json() start: {} {}".format(file_path, datetime.today()))
    
    f = open(file_path)                                                                                       
    while True:
        lines = f.readlines(10 * 1024 * 1024) # 10M 단위로 읽기                                                             
        if not lines:                                                                                                      
            break
        json_docs = [get_doc_from_line(line) for line in lines]
        for doc in json_docs:
            process_title(doc['title'])


noun_dict = process_csv_title("rmc-meta-20211104.csv")
print("### title")
for k, v  in noun_dict.items():
    print(k)
#noun_dict = process_csv_artist("rmc-meta-20211104.csv")
#print("###")
#for k, v  in noun_dict.items():
#    print(k)

#print(process_title("10억뷰 (Feat.MOON) (Mar Vista Remix)"))
#noun_list = process_artist("주진우 (JOO JIN-WOO)")

