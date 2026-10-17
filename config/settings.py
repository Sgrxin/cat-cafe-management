"""
Django settings for config project.
猫咖门店管理系统 - 毕设项目配置
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-7keydi%(pw-lgz&o@i&pykm^*p#5$2l7&mkvjneax83l54$ahd'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===== 外部服务（全部通过环境变量开启，未配置不影响运行） =====
import os
# Gmail 邮件通知（点单成功自动发信）
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# Notion 评价同步
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_REVIEW_DB = os.environ.get("NOTION_REVIEW_DB", "")
# Supabase 云数据库（可选）：配置环境变量后取消注释并注释上方 SQLite 配置
# DATABASES = {"default": {
#     "ENGINE": "django.db.backends.postgresql",
#     "NAME": os.environ.get("SUPABASE_DB_NAME", "postgres"),
#     "USER": os.environ.get("SUPABASE_DB_USER", "postgres"),
#     "PASSWORD": os.environ.get("SUPABASE_DB_PASSWORD", ""),
#     "HOST": os.environ.get("SUPABASE_DB_HOST", ""),
#     "PORT": "5432",
# }}