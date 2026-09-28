FROM docker:27-cli

RUN apk add --no-cache python3 docker-cli-compose

WORKDIR /app

COPY instancer.py cleanup.sh destroy.sh list.sh serve.sh spawn.sh ./

EXPOSE 9000

CMD ["python3", "instancer.py", "serve"]
