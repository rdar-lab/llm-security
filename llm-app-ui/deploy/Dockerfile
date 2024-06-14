# build stage
FROM node:18.18.2-alpine as build-stage
RUN apk --no-cache add build-base python3
WORKDIR /app
COPY package*.json ./
RUN npm install -g npm@9.5.1
RUN npm cache clean --force
RUN npm ci
COPY . .
ARG NODE_ENV
ENV NODE_ENV $NODE_ENV
RUN npm run build --

# production stage
FROM nginx:1.25.2-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
