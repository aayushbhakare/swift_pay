import os

from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent



SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-swiftpay-super-secret-key-2026')



DEBUG = True



ALLOWED_HOSTS = ['*']



INSTALLED_APPS = [

    'django.contrib.admin',

    'django.contrib.auth',

    'django.contrib.contenttypes',

    'django.contrib.sessions',

    'django.contrib.messages',

    'django.contrib.staticfiles',

    

    'rest_framework',

    'corsheaders',

    

    'apps.merchants',

    'apps.ledger',

    'apps.payments',

    'apps.webhooks',

    'apps.common',

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

    

    'apps.common.middleware.RedisRateLimiterMiddleware',

]



ROOT_URLCONF = 'swiftpay.urls'



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



WSGI_APPLICATION = 'swiftpay.wsgi.application'



USE_POSTGRES = os.getenv('USE_POSTGRES', 'False').lower() in ('true', '1', 'yes')



if USE_POSTGRES:

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

else:

    DATABASES = {

        'default': {

            'ENGINE': 'django.db.backends.sqlite3',

            'NAME': BASE_DIR / 'db.sqlite3',

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

    'EXCEPTION_HANDLER': 'apps.common.exceptions.custom_exception_handler',

}





REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

RATE_LIMIT_REQUESTS_PER_MINUTE = 60

RATE_LIMIT_BURST_CAPACITY = 10





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

