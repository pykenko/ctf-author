FROM ubuntu:26.04

RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 
RUN useradd -U -m -s /bin/bash mikimiku

COPY ./code /var/www/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]