# BIG UPDATE: Changed the root image and source of the configuration files for deployment
FROM node:alpine as BUILD_IMAGE
WORKDIR /app
COPY frontend/package.json ./
# install dependencies
RUN npm install --force
COPY frontend/src ./src
COPY frontend/public ./public
COPY config/frontend.env.local ./
RUN mv /app/frontend.env.local /app/.env.local
# build
RUN npm run build
FROM node:alpine
WORKDIR /app
# copy from build image
COPY --from=BUILD_IMAGE /app/package.json ./package.json
COPY --from=BUILD_IMAGE /app/node_modules ./node_modules
COPY --from=BUILD_IMAGE /app/.next ./.next
COPY --from=BUILD_IMAGE /app/public ./public
# COPY --from=BUILD_IMAGE postcss.config.js ./
# COPY --from=BUILD_IMAGE tailwind.config.js ./
COPY frontend/tailwind.config.js ./
COPY frontend/postcss.config.js ./
COPY config/frontend.env.local ./ 
RUN mv /app/frontend.env.local /app/.env.local

EXPOSE 3000
