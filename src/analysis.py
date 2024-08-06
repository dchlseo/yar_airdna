from datetime import datetime
import os
import pandas as pd
import sys
from tqdm import tqdm


def assign_file_names(directory_path):
    """AirDNA 파일 읽기"""
    monthly_file = None
    property_file = None

    # List all files in the directory
    try:
        for entry in os.scandir(directory_path):
            if entry.is_file():  # Check if the entry is a file
                full_path = os.path.join(directory_path, entry.name)  # Construct full file path
                if 'monthly' in entry.name:
                    if monthly_file is not None:
                        raise Exception("More than one 'monthly' file found.")
                    monthly_file = full_path  # Use the full path
                elif 'property' in entry.name:
                    if property_file is not None:
                        raise Exception("More than one 'property' file found.")
                    property_file = full_path  # Use the full path

    except FileNotFoundError:
        print(f"The directory {directory_path} does not exist.")
        return None, None
    except PermissionError:
        print(f"Permission denied: unable to access {directory_path}.")
        return None, None
    except Exception as e:
        print(e)
        return None, None

    if monthly_file is None or property_file is None:
        print("One or both files could not be found.")
        return None, None
    
    return monthly_file, property_file


def generate_periods(yq):
    """분석에 포함할 년월 리스트를 반환"""
    year = int(yq[:4])
    quarter = int(yq[-1])

    # 분기
    quarter_to_months = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    # 작년 동기부터 포함
    start_month = quarter_to_months[quarter][0]
    start_date = datetime(year - 1, start_month, 1)

    periods = []
    
    # 작년 동기부터 해당 분기까지 데이터 반환
    current_date = start_date
    end_month = quarter_to_months[quarter][-1]
    while True:
        #  "yyyy-mm-dd" 형태로 반환 (airdna 포맷과 일치)
        periods.append(current_date.strftime('%Y-%m-%d'))
        
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)
        
        if current_date.year == year and current_date.month > end_month:
            break
    
    return periods


def abnb_performance(data=None, month=None):
    """주요 분석 함수"""
    occ_result = []
    adr_result = []
    revpar_result = []
    
    # Subset the data for active properties with available days and matching the reporting month
    subset = data[(data['Active'] == True) & (data['Available Days'] > 0) & (data['Reporting Month'] == month)]
    subset = subset[['Property ID', 'Occupancy Rate', 'Revenue (USD)', 'ADR (USD)', 'Number of Reservations', 'Reservation Days',
                     'Available Days', 'Blocked Days', 'State', 'City', 'Active', 'Revenue (Native)', 'ADR (Native)']]
    subset = subset[subset['City'].notna()]

    subset['occ'] = subset['Occupancy Rate']
    subset['adr(usd)'] = subset['Revenue (USD)'] / subset['Reservation Days']
    subset['adr(krw)'] = subset['Revenue (Native)'] / subset['Reservation Days']
    subset['adr(krw)'] = subset['adr(krw)'].fillna(0)
    
    lower_bound = subset['adr(krw)'].quantile(0.02)
    upper_bound = subset['adr(krw)'].quantile(0.98)
    subset = subset[(subset['adr(krw)'] > lower_bound) & (subset['adr(krw)'] < upper_bound)]
    subset['revpar'] = subset['occ'] * subset['adr(krw)']
    
    region_dict = {'Gangwon-do': '강원', 'Jeju Island': '제주', 'Seoul': '서울', 'Daegu': '경북권',
                   'Busan': '부산', 'Gyeongju-si': '경남권', 'Suwon': '경기권', 'Anyang': '경기권',
                   'Chungcheongbuk-do': '충청권', 'Incheon': '경기권', 'Daejeon': '충청권', 'Gwangju': '전라권',
                   'Gyeonggi-do': '경기권', 'Seongnam': '경기권', 'Paengseong-eup': '경기권', 'Bucheon': '경기권',
                   'Jeollanam-do': '전라권', 'Jeollabuk-do': '전라권', 'Yongin': '경기권', 'Chungcheongnam-do': '충청권',
                   'Ulsan': '경남권', 'Goyang': '경기권', 'Uijeongbu': '경기권'}
    subset['Region'] = subset['City'].replace(region_dict)
    subset = subset.reset_index()

    for rg in subset['Region'].unique():
        occ_result.append([rg, subset[subset['Region'] == rg]['occ'].mean()])
        adr_result.append([rg, subset[subset['Region'] == rg]['adr(krw)'].mean()])
        revpar_result.append([rg, subset[subset['Region'] == rg]['revpar'].mean()])

    occ_result.append(['전국', subset['occ'].mean()])
    adr_result.append(['전국', subset['adr(krw)'].mean()])
    revpar_result.append(['전국', subset['revpar'].mean()])

    occ_df = pd.DataFrame(occ_result).transpose()
    adr_df = pd.DataFrame(adr_result).transpose()
    revpar_df = pd.DataFrame(revpar_result).transpose()

    # 인덱스를 연월로 변환
    year_month = f"{month[:4]}.{month[5:7]}"
    
    occ_df.columns = occ_df.iloc[0]
    adr_df.columns = adr_df.iloc[0]
    revpar_df.columns = revpar_df.iloc[0]
    
    occ_df = occ_df[1:].set_index([[year_month]])
    adr_df = adr_df[1:].set_index([[year_month]])
    revpar_df = revpar_df[1:].set_index([[year_month]])
    
    col_order = ['전국', '강원', '경기권', '경남권', '경북권', '부산', '서울', '전라권', '제주', '충청권']
    occ_df = occ_df.reindex(columns=col_order)
    adr_df = adr_df.reindex(columns=col_order)
    revpar_df = revpar_df.reindex(columns=col_order)

    return occ_df, adr_df, revpar_df


def quarter_from_month(date_str):
    """연월정보에서 분기정보 추출"""
    year, month = map(int, date_str.split('.'))
    quarter = (month - 1) // 3 + 1
    return f"{year}.Q{quarter}"


def aggregate_by_quarter(df):
    """월별데이터 분기별로 변환"""
    df2 = df.copy()
    df2.index = [quarter_from_month(idx) for idx in df.index]
    quarterly_df = df2.groupby(df2.index).mean()
    return quarterly_df


def reset_index_and_rename(df):
    """'시점' 칼럼 생성"""
    df_reset = df.reset_index().rename(columns={'index': '시점'})
    return df_reset


def run_monthly_analysis(data, periods):
    """월별 데이터 정리"""
    occ_dfs = []
    adr_dfs = []
    revpar_dfs = []

    for period in tqdm(periods, desc='RUNNING MONTHLY ANALYSIS...'):
        occ_df, adr_df, revpar_df = abnb_performance(data, month=period)
        occ_dfs.append(occ_df)
        adr_dfs.append(adr_df)
        revpar_dfs.append(revpar_df)

    return occ_dfs, adr_dfs, revpar_dfs


def aggregate_quarterly_data(occ_dfs, adr_dfs, revpar_dfs):
    """분기별 데이터 정리"""
    full_occ_df = pd.concat(occ_dfs)
    full_adr_df = pd.concat(adr_dfs)
    full_revpar_df = pd.concat(revpar_dfs)

    quarterly_occ_df = aggregate_by_quarter(full_occ_df)
    quarterly_adr_df = aggregate_by_quarter(full_adr_df)
    quarterly_revpar_df = aggregate_by_quarter(full_revpar_df)

    return quarterly_occ_df, quarterly_adr_df, quarterly_revpar_df, full_occ_df, full_adr_df, full_revpar_df


def reset_index_and_rename(df):
    """Resets the index of the DataFrame and renames the index column to '시점'."""
    df_reset = df.reset_index().rename(columns={'index': '시점'})
    return df_reset


def concatenate_and_refine_data(quarterly_df, full_df, is_occ=False):
    """OCC는 소수점 1째 자리까지 반올림, 다른 테이블은 정수로 반올림"""
    refined_df = pd.concat([quarterly_df, full_df.iloc[3:]])

    if not is_occ: 
        # adr, revpar
        refined_df.iloc[:, 1:] = refined_df.iloc[:, 1:].astype(float).round(0).astype(int)
    elif is_occ:
        # occ
        refined_df.iloc[:, 1:] = refined_df.iloc[:, 1:].astype(float) * 100
        refined_df.iloc[:, 1:] = refined_df.iloc[:, 1:].astype(float).round(1)    # NEED TO FIX: ROUNDING NOT WORKING
    
    return refined_df


def finalize_report_tables(final_adr_df, final_occ_df, final_revpar_df):
    final_adr_df['Index'] = 'ADR'
    final_occ_df['Index'] = 'OCC'
    final_revpar_df['Index'] = 'RevPAR'
    
    combined_df = pd.concat([final_adr_df, final_occ_df, final_revpar_df], ignore_index=True)
    combined_df.set_index('Index', inplace=True)
    combined_df = combined_df.reset_index()

    # 테이블값 string으로 변환 

    combined_df = combined_df.astype('str')

    return combined_df


# Main script to execute functions
def analyze_abnb(data, periods):
    occ_dfs, adr_dfs, revpar_dfs = run_monthly_analysis(data, periods)
    
    quarterly_occ_df, quarterly_adr_df, quarterly_revpar_df, full_occ_df, full_adr_df, full_revpar_df = aggregate_quarterly_data(occ_dfs, adr_dfs, revpar_dfs)
    
    # Apply reset_index_and_rename if needed here
    full_occ_df = reset_index_and_rename(full_occ_df)
    full_adr_df = reset_index_and_rename(full_adr_df)
    full_revpar_df = reset_index_and_rename(full_revpar_df)
    
    quarterly_occ_df = reset_index_and_rename(quarterly_occ_df)
    quarterly_adr_df = reset_index_and_rename(quarterly_adr_df)
    quarterly_revpar_df = reset_index_and_rename(quarterly_revpar_df)
    
    final_adr_df = concatenate_and_refine_data(quarterly_adr_df, full_adr_df)
    final_occ_df = concatenate_and_refine_data(quarterly_occ_df, full_occ_df, is_occ=True)

    # return final_occ_df

    final_revpar_df = concatenate_and_refine_data(quarterly_revpar_df, full_revpar_df)
    report_table = finalize_report_tables(final_adr_df, final_occ_df, final_revpar_df)
    
    print('COMPLETE.')

    return report_table


def save_data(df, filepath, codec='cp949'):

    df.to_csv(filepath, encoding=codec)
    print(f'ENCODING: {codec}')
    print(f'DATA SAVED: {filepath}')
    