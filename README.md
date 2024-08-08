# yar_airdna

## Overview
- 야놀자리서치 분기동향보고서 "공유숙박" 파트 원데이터 정제/분석/저장 워크플로우를 자동화한 프로그램
    - 1) AWS 모듈: AWS 접속, 데이터 로컬에 저장
    - 2) 분석 모듈: 로컬에 저장된 데이터의 정제/분석, 결과 테이블 저장

작업을 위한 모든 설정값은 config.json 파일 참고.
프로그램은 터미널에서 실행.

## Prerequisites
설정(Configuration)
- config.json 파일 설정
    - "AWS_ACCESS_KEY_ID": AWS id 값,
    - "AWS_SECRET_ACCESS_KEY": AWS 비밀번호,
    - "BUCKET_NAME": AWS 저장소("airdna-prod-data-integration"),
    - "BASE_PREFIX": 다운로드할 데이터 디렉토리(예: 'yanolja/outbound/'),
    - "DATA_DIRECTORY": 데이터 저장할 로컬 디렉토리(예: 'data/'),
    - "P_YM": 다운로드할 데이터 연월(예: '2024-06-01'),
    - "YQ": 분석할 데이터 연/분기(예: '2024q2'),
    - "EXTENSION": 데이터 저장 포맷('.xlsx'),
    - "CODEC": 데이터 인코딩 포맷 ('cp949')

개발 환경
- Python 3.11
- 패키지 설치

```bash
    pip install -r requirements.txt
```

## Execution
다음의 세 가지 옵션 중 택1하여 프로그램을 실행 (터미널에 코드 실행)
1. 전체 프로그램 실행 ("all")
```bash
    python airdna_main.py all
```

2. 데이터 다운로드만 실행 ("download")
```bash
    python airdna_main.py download
```

3. 데이터 분석만 실행 ("analysis")
```bash
    python airdna_main.py analysis
```

## Output
- 분기동향보고서 뒷편의 데이터 테이블 형태로 출력 (기본 확장자 '.xlsx'로 세팅)

  