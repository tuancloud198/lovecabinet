import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'development-only-change-before-deploy')
DEBUG = os.environ.get('DEBUG', '0') == '1'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,backend,testserver').split(',')
INSTALLED_APPS = ['django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'rest_framework', 'rest_framework.authtoken', 'users', 'couple_invitations', 'couples', 'cabinets', 'jars', 'memories', 'photos', 'events']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware']
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
if os.environ.get('POSTGRES_HOST'):
    DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', 'HOST': os.environ['POSTGRES_HOST'], 'PORT': os.environ.get('POSTGRES_PORT', '5432'), 'NAME': os.environ.get('POSTGRES_DB', 'lovecabinet'), 'USER': os.environ.get('POSTGRES_USER', 'lovecabinet'), 'PASSWORD': os.environ['POSTGRES_PASSWORD'], 'CONN_MAX_AGE': 60, 'CONN_HEALTH_CHECKS': True}}
    if os.environ.get('POSTGRES_SSLMODE'):  # e.g. 'require' for Amazon RDS
        DATABASES['default']['OPTIONS'] = {'sslmode': os.environ['POSTGRES_SSLMODE']}
AUTH_USER_MODEL = 'users.User'
# OAuth 2.0 Web client ID from Google Cloud Console; empty disables "Sign in with Google".
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication'], 'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'], 'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle'], 'DEFAULT_THROTTLE_RATES': {'anon': '60/hour'}}
# Reverse proxies in front of Django (compose: nginx = 1; EKS: ALB + nginx = 2). Lets the anonymous
# rate limit see each client's own IP from X-Forwarded-For instead of the proxy's.
if os.environ.get('TRUSTED_PROXY_COUNT'):
    REST_FRAMEWORK['NUM_PROXIES'] = int(os.environ['TRUSTED_PROXY_COUNT'])
USE_TZ = True
TIME_ZONE = 'Asia/Ho_Chi_Minh'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# S3-compatible object storage: MinIO by default. For Amazon S3, set MINIO_ENDPOINT and the keys to empty
# strings to use AWS's endpoint and default credentials (e.g. an IAM role for the service account).
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'http://localhost:9000') or None
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'lovecabinet') or None
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'local-minio-password') or None
MINIO_BUCKET = os.environ.get('MINIO_BUCKET', 'memories')
MINIO_REGION = os.environ.get('MINIO_REGION', 'us-east-1')
DATA_UPLOAD_MAX_MEMORY_SIZE = 12 * 1024 * 1024
