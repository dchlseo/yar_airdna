import boto3
from datetime import datetime
import json
import os


def load_config():
    """config 파일 읽기"""
    with open('../config.json', 'r') as file:
        config = json.load(file)
    return config


def display_config(aws_access_key_id, aws_secret_access_key):
    """config 파일 내의 민감 정보(aws id, key) 마스킹 후 표시"""
    def mask_string(s):
        if len(s) > 6:
            return s[:3] + '*' * (len(s) - 6) + s[-3:]
        else:
            return '*' * len(s)
    
    return mask_string(aws_access_key_id), mask_string(aws_secret_access_key)
        

def convert_date_format(date_str):
    """입력날짜 포맷 변경 (2024-06-01 --> June 2024)"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%B %Y")
    
    return formatted_date


def init_s3_client(aws_access_key_id, aws_secret_access_key):
    """Initialize and return an S3 client."""
    s3_client = boto3.client(
        's3', 
        aws_access_key_id=aws_access_key_id, 
        aws_secret_access_key=aws_secret_access_key
    )
    return s3_client


def airdna_data_download(s3, base_prefix, bucket_name, ml):
    """Set local directory and download data"""
    prefix = base_prefix + ml
    response = s3.list_objects_v2(Bucket = bucket_name, Prefix = prefix)
    
    if 'Contents' in response:
        directory_path = '../data/' + ml
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created.")
        else:
            print(f"Directory '{directory_path}' already exists.")
        
        files = []
        for obj in response['Contents']:
            files.append(obj['Key'])
        print(files)
        for i in range(1, len(files)):   # data files (.csv)
            object_key = files[i]
            local_file_path = directory_path + '/' + object_key.split('/')[3]
            print(f'DOWNLOADING FILE: {object_key}...')

            # download data
            s3.download_file(bucket_name, object_key, local_file_path)
            
            print('DOWNLOAD COMPLETE.')

    else:
        print("No objects found in the specified bucket and prefix.")