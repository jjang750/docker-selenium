# SSG 랜더스 일정 텔레그램 전송용 단발성 실행 이미지 (docker run --rm 으로 1회 실행)
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# TZ=Asia/Seoul 환경변수가 datetime.now() 에 반영되도록 tzdata 설치
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

ENTRYPOINT ["python3", "main.py"]
