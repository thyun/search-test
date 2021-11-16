# https://gist.github.com/sysboss/d40ea8a7a12f510e61d7980269323b36
# https://danbernstein.netlify.app/post/2021-01-08-enhancing-aws-athena-with-python/
#
# Query AWS Athena using SQL
# Copyright (c) Alexey Baikov <sysboss[at]mail.ru>
#
# This snippet is a basic example to query Athen and load the results
# to a variable.
#
# Requirements:
# > pip3 install boto3 botocore retrying
import os
import sys
import csv
import boto3
import botocore
from retrying import retry
import datetime
from datetime import date, timedelta

# configuration
s3_bucket = 'prod-srch-seoul-glue-batch'       # S3 Bucket name
s3_key_prefix = 'output'
s3_ouput  = 's3://' + s3_bucket + '/' + s3_key_prefix # S3 Bucket to store results
database  = 'searchdb'  # The database to which the query belongs

# init clients
athena = boto3.client('athena')
s3     = boto3.resource('s3')

@retry(stop_max_attempt_number = 10,
    wait_exponential_multiplier = 300,
    wait_exponential_max = 1 * 60 * 1000)
def poll_status(_id):
    result = athena.get_query_execution( QueryExecutionId = _id )
    state  = result['QueryExecution']['Status']['State']

    if state == 'SUCCEEDED':
        return result
    elif state == 'FAILED':
        return result
    else:
        raise Exception

def run_query(query, database, s3_output):
    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': s3_output,
    })

    QueryExecutionId = response['QueryExecutionId']
    result = poll_status(QueryExecutionId)

    if result['QueryExecution']['Status']['State'] == 'SUCCEEDED':
        #print("Query SUCCEEDED: {}".format(QueryExecutionId))

        s3_key = s3_key_prefix + '/' + QueryExecutionId + '.csv'
        local_filename = QueryExecutionId + '.csv'

        # download result file
        try:
            s3.Bucket(s3_bucket).download_file(s3_key, local_filename)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise

        # read file to array
        rows = []
        with open(local_filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rows.append(row)

        # delete result file
        if os.path.isfile(local_filename):
            os.remove(local_filename)

        return rows

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def run_day(target_date):
    start_time = target_date + '00'
    end_time = target_date + '23'

    # SQL Query to execute
    query = ("""
SELECT count(message.keyword) as message_count
FROM searchdb.keyword where part_hour between '%s' and '%s' and message.channel = 'ohsara'
    """)

    #print("Executing query: {}".format(query))
    result = run_query(query % (start_time, end_time), database, s3_ouput)

    print(f"{target_date}, {result[0]['message_count']}")
    #print(target_date, ",", result[0]['message_count'])

def run_period():
    start_date = date(2021, 8, 17)
    end_date = date(2021, 11, 1)
    
    for dt in daterange(start_date, end_date):
        target_date = dt.strftime("%Y%m%d")
        run_day(target_date)

if __name__ == '__main__':
    run_period()
