"""
生产环境配置
"""
from .base import *

DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'zhongyue'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'mysql'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Security settings
SECURE_SSL_REDIRECT = False  # 修改为False，除非你确实使用了HTTPS
SESSION_COOKIE_SECURE = False  # 修改为False，除非你确实使用了HTTPS
CSRF_COOKIE_SECURE = False  # 修改为False，除非你确实使用了HTTPS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CORS settings
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'access_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/data/apps/web/logs/zhongyue-django/access.log',
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/data/apps/web/logs/zhongyue-django/error.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'access_file', 'error_file'],
        'level': 'INFO',
    },
}

# MinIO生产环境配置
AWS_ACCESS_KEY_ID = os.environ.get('MINIO_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('MINIO_SECRET_KEY')
AWS_S3_ENDPOINT_URL = os.environ.get('MINIO_ENDPOINT_URL', 'http://minio:9000')
MEDIA_URL = os.environ.get('MINIO_MEDIA_URL', f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/')
AWS_S3_USE_SSL = os.environ.get('MINIO_USE_SSL', 'false').lower() == 'true'

# 生产环境特定的S3配置
AWS_S3_CUSTOM_DOMAIN = os.environ.get('MINIO_CUSTOM_DOMAIN')  # 如果有自定义域名