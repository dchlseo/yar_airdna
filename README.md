# yar_airdna

## Summary
- 야놀자리서치 분기동향보고서 "공유숙박" 파트 원데이터 정제/분석/저장 워크플로우를 자동화한 프로그램
    - 1) AWS 모듈: AWS 접속, 데이터 로컬에 저장
    - 2) 분석 모듈: 로컬에 저장된 데이터의 정제/분석, 결과 테이블 저장

작업을 위한 모든 설정값은 config.json 파일 참고.

## Prerequisites
설정
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


```python
    pip install -r requirements.txt
