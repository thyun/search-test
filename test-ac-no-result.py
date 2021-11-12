import http.client # python3에서 httplib -> http.client 로 변경됨. class는 동일
from urllib import parse
import json
import csv
import sys
import os
import time

PROGRAM = "test-ac-no-result"

# op env

# dev env
API_HOST = "pri-api.srch.skplanetx.com"
API_PORT = 80
API_PATH = "/api/smartwallet/1.0/search/all.json"

#if len(sys.argv) == 1:
#	print "Usage:"
#	print "%s {YYYY.MM.DD} {TrackingCode}" % PROGRAM
#	print "ex) %s 2017.01.01 \"search_filter_test\\\\\\\\|83\\\\\\\\|1\\\\\\\\|A\"" % PROGRAM
#	sys.exit()

#dt = sys.argv[1]
#tcs = [sys.argv[2]]
#index = "event-" + dt

rqbody = """
{
}
"""

rsbody = """
"""

# Make connection, csv writer
conn = http.client.HTTPConnection(API_HOST, API_PORT)
output = csv.writer(sys.stdout)
#output = csv.writer(open("test.csv", "wb+"))

# Loop for syrup_keyword.csv
file_name = "syrup_keyword.csv"
count = 0
for l in open(file_name, encoding="utf8", errors='ignore'):
    nl = l.rstrip()
    tokens = nl.split(',')

	# Send http request
    query = [('q', tokens[0])]
    url = API_PATH + "?" + parse.urlencode(query)
    #print(url)
    conn.request("GET", url)
    response = conn.getresponse()
    rsbody = response.read()
	#print response.status, response.reason
	#print(rsbody)

	# Parse response
    jo = json.loads(rsbody)
    response = jo["response"]
    total = response["card"]["num_found"] + response["brand"]["num_found"] + response["coupon"]["num_found"] + response["event"]["num_found"] + response["mirizum"]["num_found"]
    if total>0:
        print(nl)
    count += 1
    if (count % 100 == 0):
        print("count", count, "sleeping")
        time.sleep(10)

sys.exit()

