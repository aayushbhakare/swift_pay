import os

from pathlib import Path

from dotenv import load_dotenv



BASE_DIR = Path(__file__).resolve().parent.parent





load_dotenv(BASE_DIR / '.env')



SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-swiftpay-super-secret-key-2026')



DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')



ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')



INSTALLED_APPS = [

    'django.contrib.admin',

    'django.contrib.auth',

    'django.contrib.contenttypes',

    'django.contrib.sessions',

    'django.contrib.messages',

    'django.contrib.staticfiles',

    

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',

    'rest_framework_simplejwt',
    'django_filters',

    

    'swiftpay.merchants',
    'swiftpay.payments',
    'swiftpay.authentication',
    'swiftpay.webhooks',

]



MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]



ROOT_URLCONF = 'backend.urls'



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



WSGI_APPLICATION = 'backend.wsgi.application'



DATABASES = {

    'default': {

        'ENGINE': 'django.db.backends.postgresql',

        'NAME': os.getenv('DB_NAME', 'swiftpay_db'),

        'USER': os.getenv('DB_USER', 'postgres'),

        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),

        'HOST': os.getenv('DB_HOST', '127.0.0.1'),

        'PORT': os.getenv('DB_PORT', '5432'),

    }

}





AUTH_PASSWORD_VALIDATORS = []



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



REST_FRAMEWORK = {

    'DEFAULT_RENDERER_CLASSES': [

        'rest_framework.renderers.JSONRenderer',

    ],

    'DEFAULT_PARSER_CLASSES': [

        'rest_framework.parsers.JSONParser',

    ],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'swiftpay.authentication.authentication.APIKeyAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '10/second',
        'user': '10/second'
    },

}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')

# Twilio Settings
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_FROM_NUMBER = os.getenv('TWILIO_FROM_NUMBER', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', '')



REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

RATE_LIMIT_REQUESTS_PER_MINUTE = 60

RATE_LIMIT_BURST_CAPACITY = 10

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:8000').split(',') if origin.strip()]
CORS_ALLOW_HEADERS = ['*']




LOGGING = {

    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {

        'verbose': {

            'format': '[{asctime}] {levelname} [{name}:{lineno}] {message}',

            'style': '{',

        },

    },

    'handlers': {

        'console': {

            'class': 'logging.StreamHandler',

            'formatter': 'verbose',

        },

    },

    'loggers': {

        'swiftpay': {

            'handlers': ['console'],

            'level': 'INFO',

            'propagate': True,

        },

        'apps': {

            'handlers': ['console'],

            'level': 'INFO',

            'propagate': True,

        },

    },

}

