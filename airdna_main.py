import sys
import os
import pandas as pd
from datetime import datetime
from src import aws_utils as aws
from src import analysis as ans


def print_config(aws_access_key_id, aws_secret_access_key, bucket_name, full_path, p_ym, yq, file_format, codec):
    """ Print configuration settings. """
    masked_id, masked_key = aws.display_config(aws_access_key_id, aws_secret_access_key)
    print('----------------------------CONFIG----------------------------')
    print(f"AWS_ACCESS_KEY_ID: {masked_id}")
    print(f"AWS_SECRET_ACCESS_KEY: {masked_key}")
    print(f"BUCKET_NAME: {bucket_name}")
    print(f"DATA_DIRECTORY: {full_path}")
    print(f"P_YM: {p_ym}")
    print(f"QUARTER: {yq}")
    print(f"SAVE_FORMAT: {file_format}")
    print(f'OUTPUT_CODEC: {codec}')
    print('---------------------------------------------------------------')


def download_data(aws_access_key_id, aws_secret_access_key, base_prefix, bucket_name, output_date):
    """ Download data from AWS S3. """
    start_time = datetime.now()
    print("START TIME:", start_time.time())
    s3 = aws.init_s3_client(aws_access_key_id, aws_secret_access_key)
    aws.airdna_data_download(s3=s3, base_prefix=base_prefix, bucket_name=bucket_name, ml=output_date)
    end_time = datetime.now()
    print("END TIME:", end_time.time())
    print('DOWNLOAD COMPLETE.')
    print(f'RUNTIME: {end_time - start_time}')


def perform_analysis(full_path, yq, file_format, codec):
    """ Perform data analysis and save results. """
    start_time = datetime.now()
    monthly_file, property_file = ans.assign_file_names(full_path)
    # df_property = pd.read_csv(property_file, dtype={56: 'str'})
    df_performance = pd.read_csv(monthly_file, dtype={18: 'str', 26: 'str', 27: 'str', 28: 'str'})
    periods = ans.generate_periods(yq)
    full_table = ans.analyze_abnb(df_performance, periods)
    filename = 'abnb_' + yq
    filepath = os.path.join(full_path, filename + '.' + file_format)
    ans.save_data(full_table, filepath, file_format=file_format, codec=codec)
    end_time = datetime.now()
    print("END TIME:", end_time.time())
    print(f'RUNTIME: {end_time - start_time}')
    print('RESULTS:')
    print(full_table)


def main(operation='all'):
    """ Main function to handle data processing based on operation mode.
    
    Args:
        operation (str): Operation mode ('all', 'download', or 'analysis').
    """
    try:
        # Load configuration and set up
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
        full_path = os.path.join(data_dir, output_date)


        print_config(aws_access_key_id, aws_secret_access_key, bucket_name, full_path, p_ym, yq, file_format, codec)

        print(f'OPERATION: {operation}')

        if operation in ['all', 'download']:
            print('DOWNLOADING DATA FROM AWS')
            download_data(aws_access_key_id, aws_secret_access_key, base_prefix, bucket_name, output_date)

        if operation in ['all', 'analysis']:
            print('PERFORMING ANALYSIS')
            perform_analysis(full_path, yq, file_format, codec)

    except Exception as e:
        print(f"Error during operation {operation}: {str(e)}")


if __name__ == '__main__':
    operation_mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    main(operation_mode)
