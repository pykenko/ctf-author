FROM ubuntu:latest

RUN apt-get update && apt-get install -y socat gcc && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN useradd -U -m -s /bin/bash ctf
RUN apt-get update && apt-get install -y gcc-multilib

COPY ./chall.c /home/ctf/chall.c
COPY ./run.sh /home/ctf/run
COPY ./kronichiwa.hololive /home/ctf/kronichiwa.hololive

RUN chown -R root:ctf /home/ctf && chmod -R 550 /home/ctf

WORKDIR /home/ctf/
RUN gcc -m32 -fno-stack-protector chall.c -o chall
RUN apt-get purge -y gcc && rm -rf /home/ctf/chall.c

CMD socat TCP-L:38932,fork EXEC:"/home/ctf/run",reuseaddr,stderr