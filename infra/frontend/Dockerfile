# Frontend image (Vue build served by nginx, which proxies /api/ to the backend). Build from the repo root:
#   docker build -f infra/frontend/Dockerfile -t lovecabinet-frontend .
# Set BACKEND_URL to where the backend is reachable (default http://backend:8000).
FROM node:22-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
# Shown in the app (Profile) to check which release is running: --build-arg APP_VERSION=0.2.6
ARG APP_VERSION=dev
RUN VITE_APP_VERSION=$APP_VERSION npm run build

FROM nginx:1.27-alpine
ENV BACKEND_URL=http://backend:8000
# nginx renders templates with the container's env vars at startup.
COPY infra/frontend/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
