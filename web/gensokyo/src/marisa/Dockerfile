FROM node:20-bullseye-slim

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm install --legacy-peer-deps

COPY app ./app
COPY marisa.png ./

RUN npm run build

EXPOSE 3000
CMD ["npm","start"]
