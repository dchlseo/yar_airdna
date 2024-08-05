import boto3
from datetime import datetime
import json
import os
import pandas as pd
import sys
from src import aws_utils as aws


def main():
    # SETUP
    config = aws.load_config()
    aws_access_key_id = config['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = config['AWS_SECRET_ACCESS_KEY']
    bucket_name = config['BUCKET_NAME']
    base_prefix = config['BASE_PREFIX']
    data_dir = config['DATA_DIRECTORY']
    p_ym = config['P_YM']

    output_date = aws.convert_date_format(p_ym)
    bucket_dir = base_prefix + output_date

    masked_id, masked_key = aws.display_config(aws_access_key_id, aws_secret_access_key)   # 민감정보 가리기

    print('----------------------------CONFIG----------------------------')
    print(f"AWS_ACCESS_KEY_ID: {masked_id}")
    print(f"AWS_SECRET_ACCESS_KEY: {masked_key}")
    print(f"BUCKET_NAME: {bucket_name}")
    print(f"BUCKET_DIR: {bucket_dir}")
    print(f"DATA_DIRECTORY: {data_dir}")
    print(f"P_YM: {p_ym}")
    print('---------------------------------------------------------------')

    start_time = datetime.now()
    print("START TIME:", start_time.time())


    # AWS S3 스토리지 접속 & 데이터 다운로드
    print("Accessing AWS Storage...")
    aws_access_key_id = config['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = config['AWS_SECRET_ACCESS_KEY']

    s3 = aws.init_s3_client(aws_access_key_id, aws_secret_access_key)
    print('Accessed S3 storage: ', s3)

    print('Start data download...')
    aws.airdna_data_download(s3=s3, base_prefix=base_prefix, bucket_name=bucket_name, ml=output_date)

    end_time = datetime.now()
    print("END TIME:", end_time.time())

    print('DOWNLOAD COMPLETE.')
    print(f'RUNTIME: {end_time - start_time}')


if __name__ == '__main__':
    main()
