# Backend image (Django + gunicorn). Build from the repo root:
#   docker build -f infra/backend/Dockerfile -t lovecabinet-backend .
# PostgreSQL and object storage are separate services; point the container at them with env vars:
#   SECRET_KEY, ALLOWED_HOSTS, POSTGRES_HOST/PORT/DB/USER/PASSWORD (POSTGRES_SSLMODE=require for RDS),
#   MINIO_ENDPOINT/ACCESS_KEY/SECRET_KEY/BUCKET/REGION (empty endpoint + keys = Amazon S3 with an IAM role).
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Shown in the app (Profile) to check which release is running: --build-arg APP_VERSION=0.2.4
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION
WORKDIR /app
COPY backend/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt
COPY backend/ .
RUN useradd --uid 10001 --create-home app && chown -R app:app /app
USER 10001
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "90"]
