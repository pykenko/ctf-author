FROM node:18

WORKDIR /app

COPY server.js .

RUN apt-get update && apt-get install -y python3 make g++ \
    && rm -rf /var/lib/apt/lists/*

RUN npm install express better-sqlite3

CMD ["node", "server.js"]
