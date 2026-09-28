FROM ubuntu:26.04

RUN apt-get update && \
    apt-get install -y xinetd python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /etc/xinetd.d/*

RUN useradd -U -m -s /bin/bash maimai

COPY ./xinetd.conf /etc/xinetd.d/chall
RUN chmod 644 /etc/xinetd.d/chall

COPY ./server.py /home/maimai/server.py
COPY ./flag.txt /home/maimai/flag.txt

RUN chown -R root:maimai /home/maimai && chmod -R 550 /home/maimai

EXPOSE 3134

CMD ["xinetd", "-dontfork", "-stayalive"]
