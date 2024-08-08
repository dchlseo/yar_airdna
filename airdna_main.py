import boto3
from datetime import datetime
import json
import os
import pandas as pd
import sys
from src import aws_utils as aws
from src import analysis as ans


def main():
    # SETUP
    config = aws.load_config('config.json')
    aws_access_key_id = config['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = config['AWS_SECRET_ACCESS_KEY']
    bucket_name = config['BUCKET_NAME']
    base_prefix = config['BASE_PREFIX']
    data_dir = config['DATA_DIRECTORY']
    p_ym = config['P_YM']
    yq = config['YQ']
    file_format = config['EXTENSION']
    codec = config["CODEC"]

    output_date = aws.convert_date_format(p_ym)
    bucket_dir = base_prefix + output_date
    full_path = os.path.join(data_dir, output_date)

    masked_id, masked_key = aws.display_config(aws_access_key_id, aws_secret_access_key)   # 민감정보 가리기

    print('----------------------------CONFIG----------------------------')
    print(f"AWS_ACCESS_KEY_ID: {masked_id}")
    print(f"AWS_SECRET_ACCESS_KEY: {masked_key}")
    print(f"BUCKET_NAME: {bucket_name}")
    print(f"BUCKET_DIR: {bucket_dir}")
    print(f"DATA_DIRECTORY: {full_path}")
    print(f"P_YM: {p_ym}")
    print(f"QUARTER: {yq}")
    print(f"SAVE_FORMAT: {file_format}")

    print('---------------------------------------------------------------')

    start_time = datetime.now()
    print("START TIME:", start_time.time())


    # Step 1: AWS S3 스토리지 접속 & 데이터 다운로드
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


    # Step 2: Airbnb performance 분석 & 최종 테이블 생성
    print('Reading abnb data...')
    start_time = datetime.now()
    print("START TIME:", start_time.time())

    monthly_file, property_file = ans.assign_file_names(full_path)
    print(f'READING: {property_file}')
    df_property = pd.read_csv(property_file, dtype={56: 'str'})
    print(f'READING: {monthly_file}')
    df_performance = pd.read_csv(
        monthly_file,
        dtype={
            18: 'str',
            26: 'str', 
            27: 'str',
            28: 'str'  
        }
    )
    print('DATA IMPORT COMPLETE.')

    periods = ans.generate_periods(yq)
    print(f'PERIODS:')
    for p in periods:
        print(f'- {p}')

    # AirDNA 데이터 분석
    full_table = ans.analyze_abnb(df_performance, periods)

    # 데이터 저장
    filename = 'abnb_' + yq
    filepath = os.path.join(full_path, filename + '.' + file_format)
    ans.save_data(full_table, filepath, file_format=file_format)

    end_time = datetime.now()
    print("END TIME:", end_time.time())
    print(f'RUNTIME: {end_time - start_time}')


if __name__ == '__main__':
    main()
