FROM ubuntu:latest

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN apt update --fix-missing && apt install libseccomp-dev python3 python3-pip socat -y

RUN groupadd -r ctf && useradd -r -g ctf ctf

ENV TERM=linux
ENV TERMINFO=/etc/terminfo

WORKDIR /home/ctf

COPY ./auric.py .
COPY ./server.py .
COPY ./chat.txt .
COPY ./user.db .
COPY ./docs .

RUN chmod 440 /home/ctf/chat.txt
RUN chmod 440 /home/ctf/user.db
RUN chmod 550 /home/ctf/server.py
RUN chmod 550 /home/ctf/auric.py

RUN echo '#!/bin/bash' > /home/ctf/run \
    && echo 'cd /home/ctf && exec python3 server.py' >> /home/ctf/run
RUN chmod 750 /home/ctf/run

RUN chown -R root:ctf /home/ctf

EXPOSE 16961

CMD socat TCP-L:16961,fork EXEC:"/home/ctf/run",reuseaddr,stderr