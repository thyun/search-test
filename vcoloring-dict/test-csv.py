import os
import sys
import csv
import boto3
import botocore
from retrying import retry

local_filename = 'rmc_meta_20211104.csv'
with open(local_filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print(row['artist'])

