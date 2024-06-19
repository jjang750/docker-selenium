가상환경 생성 [linux]
> python -m venv ${NAME}

가상환경 활성화 [linux]
> source ${NAME}/bin/activate

app 폴더의 DockerFile 실행
> docker build -t chrome-cron .

docker 실행 시 env 파라미터 필요
> docker run -e TELEGRAM_TOKEN=${TELEGRAM TOKEN} -e TELEGRAM_CHAT_ID=${CHAT ID} chrome-cron:latest

