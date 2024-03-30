FROM node:21-alpine

WORKDIR /app

COPY package.json ./
COPY postcss.config.js ./
COPY tailwind.config.js ./
COPY node_modules ./

RUN npm install --save-dev
