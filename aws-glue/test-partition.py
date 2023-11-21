import boto3
from datetime import datetime, timedelta
import time
import os

ENV = 'dev'
DATABASE = 'searchdb'
BUCKET_DATARAKE = 'dev-srch-seoul-datalake'
BUCKET_GLUE = 'dev-srch-seoul-glue-batch'
HOUR_LIST = [i for i in range(0, 24)]
os.environ['TZ'] = 'Asia/Seoul'
time.tzset()

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

def setPartitionDay(target_date):
    part_day = target_date.strftime("%Y%m%d")
    year = target_date.year
    month = target_date.month
    day = target_date.day

    print(f'setPartition: part_day={part_day} year={year} month={month} day={day}')
    client = boto3.client('athena')
    for hour in HOUR_LIST:
        query = f'alter table searchdb.keyword add if not exists partition(part_hour="{part_day}{hour:02d}") location "s3://{BUCKET_DATARAKE}/search-log/raw/{year}/{month:02d}/{day:02d}/{hour:02d}";'

        # Execution
        response = client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': f'{DATABASE}'
            },
            ResultConfiguration={
                'OutputLocation': f's3://{BUCKET_GLUE}/temp',
            }
        )
    time.sleep(1);

def setPartition(start_date, end_date):
    for target_date in daterange(start_date, end_date):
        setPartitionDay(target_date)

def setPartition4Str(start_day, end_day):
    start_date = datetime.strptime(start_day, "%Y%m%d")
    end_date = datetime.strptime(end_day, "%Y%m%d")
    setPartition(start_date, end_date)

def setPartition4Period(target_date, period_day):
    start_date = target_date - timedelta(days=period_day)
    end_date = target_date - timedelta(days=1)
    setPartition(start_date, end_date)

setPartition4Str('20231101', '20231121')

