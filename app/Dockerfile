FROM chrome-cron:latest
USER root

WORKDIR /app
COPY *.py /app/
COPY run.sh /app/run.sh
RUN chmod +x /app/run.sh
ENTRYPOINT ["/app/run.sh"]
