import sys
import os
import pandas as pd
from datetime import datetime
from src import aws_utils as aws   # 다운로드 모듈
from src import analysis as ans   # 분석 모듈

"""
중요: 프로그램 실행 전 config.json 파일 확인 후 파라미터 값 제대로 세팅되어 있는지 확인!
    "AWS_ACCESS_KEY_ID": AWS id 값,
    "AWS_SECRET_ACCESS_KEY": AWS 비밀번호,
    "BUCKET_NAME": AWS 저장소,
    "BASE_PREFIX": 다운로드할 데이터 디렉토리,
    "DATA_DIRECTORY": 저장할 데이터 디렉토리 (로컬),
    "P_YM": 다운로드할 데이터 연월,
    "YQ": 분석할 데이터 연/분기,
    "EXTENSION": 데이터 저장 포맷(확장자명),
    "CODEC": 데이터 인코딩

"""


def print_config(aws_access_key_id, aws_secret_access_key, bucket_name, full_path, p_ym, yq, file_format, codec):
    """ config 파일 출력 (민감 정보 마스킹)"""
    masked_id, masked_key = aws.display_config(aws_access_key_id, aws_secret_access_key)   # aws id, key masking
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
    """ 
    AWS S3에서 Airbnb 데이터 다운로드
    참고: 
        AirDNA에서 월초에 한번씩 데이터 업데이트. 
        다운받고자 하는 월 데이터는 config의 'p_ym' 값으로 설정 (예: 2024년 6월 데이터는 p_ym = '2024-06-01')
    """

    start_time = datetime.now()
    print("START TIME:", start_time.time())
    s3 = aws.init_s3_client(aws_access_key_id, aws_secret_access_key)
    aws.airdna_data_download(s3=s3, base_prefix=base_prefix, bucket_name=bucket_name, ml=output_date)
    end_time = datetime.now()
    print("END TIME:", end_time.time())
    print('DOWNLOAD COMPLETE.')
    print(f'RUNTIME: {end_time - start_time}')


def perform_analysis(full_path, yq, file_format, codec):
    """ 로컬에 저장된 데이터 파일 불러와서 분석, 결과 테이블 저장. """
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
    """ 
    실행 코드
    
    Args:
        operation (str): Operation mode ('all', 'download', or 'analysis').
        'all': 1) AWS에서 데이터 다운로드 후, 2) 분석/결과저장
        'download': 1) AWS에서 데이터 다운로드 후 프로그램 중지
        'analysis': 2) 분석/결과저장 (로컬에 데이터 저장되어 있어야 함)
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
