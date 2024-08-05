import boto3
from datetime import datetime
import gzip
import json
import logging
import os
import shutil


def load_config():
    """config 파일 읽기"""
    with open('config.json', 'r') as file:
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


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def airdna_data_download(s3, base_prefix, bucket_name, ml):
    """Set local directory and download data"""
    prefix = base_prefix + ml
    try:
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    except Exception as e:
        logging.error(f"Failed to list objects: {e}")
        return
    
    if 'Contents' in response:
        directory_path = 'data/' + ml
        os.makedirs(directory_path, exist_ok=True)
        logging.info(f"Directory set up at '{directory_path}'")
        
        files = [obj['Key'] for obj in response['Contents'] if obj['Key'] != prefix]
        for object_key in files:
            local_file_path = os.path.join(directory_path, object_key.split('/')[-1])
            try:
                # MODIFY HERE TO DOWNLOAD ONLY CSV
                logging.info(f'DOWNLOADING FILE: {object_key}...')
                logging.info(f'SAVE DIRECTORY: {local_file_path}')
                s3.download_file(bucket_name, object_key, local_file_path)
                logging.info('DOWNLOAD COMPLETE.')
                
                if local_file_path.endswith('.gz'):
                    uncompressed_file_path = local_file_path[:-3]
                    with gzip.open(local_file_path, 'rb') as f_in:
                        with open(uncompressed_file_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    logging.info(f'File decompressed: {uncompressed_file_path}')
                    os.remove(local_file_path)
                    logging.info(f'Removed compressed file: {local_file_path}')
            except Exception as e:
                logging.error(f"Error handling file {object_key}: {e}")
    else:
        logging.warning("No objects found in the specified bucket and prefix.")
