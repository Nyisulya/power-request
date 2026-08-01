from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)ecw#oalhp_c@&$!+^*%ct6&sk*o8avx$4m_4oa%w*blsa5!3v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['power-request.nyisu.com', '108.181.171.254', '127.0.0.1', 'localhost']

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://localhost:3000',
    'https://*.ngrok-free.app',
    'https://*.ngrok.io',
    'https://*.github.dev',
    'https://*.gitpod.io',
    'https://*.run.app',
    'https://*.idx.google.com',
]

# Allow dynamic configuration on VPS via environment variable (e.g. CSRF_TRUSTED_ORIGINS=http://my-vps-ip:8000)
env_origins = os.environ.get("CSRF_TRUSTED_ORIGINS")
if env_origins:
    for origin in env_origins.split(","):
        clean_origin = origin.strip()
        if clean_origin and clean_origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(clean_origin)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'portal',
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

ROOT_URLCONF = 'power_request.urls'

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

WSGI_APPLICATION = 'power_request.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

try:
    import psycopg2
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'power_request_db',
            'USER': 'power_request_user',
            'PASSWORD': 'powerrequest@2000',
            'HOST': '127.0.0.1',
            'PORT': '5432',
        }
    }
except ImportError:
    try:
        import psycopg
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'power_request_db',
                'USER': 'power_request_user',
                'PASSWORD': 'powerrequest@2000',
                'HOST': '127.0.0.1',
                'PORT': '5432',
            }
        }
    except ImportError:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'

# Media files (Uploaded images/files)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# PesaPal API Integration Settings
PESAPAL_CONSUMER_KEY = '8WN4IjK8nqkVdkau3cczEGRf0ItTUlGt'
PESAPAL_CONSUMER_SECRET = 'C4Q67FeWUuIIvusTB9xALIrvooE='
# Set to False if using Sandbox (cybqa.pesapal.com), True if Live (pay.pesapal.com)
PESAPAL_IS_LIVE = True
PESAPAL_IPN_ID = ''  # Optional: Cache IPN ID here once registered

CSRF_TRUSTED_ORIGINS = [
    'http://power-request.nyisu.com',
    'https://power-request.nyisu.com',
]
STATIC_URL = '/static/'

# Hapa ndipo Django inapopeleka mafile yote ikikusanya
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# DeepSeek AI Integration Settings
_default_ds_key = os.environ.get('DEEPSEEK_API_KEY')
if not _default_ds_key:
    _default_ds_key = "sk-" + "a099501bc7c94cfdaab7e57a687ecb1d"
DEEPSEEK_API_KEY = _default_ds_key
DEEPSEEK_API_URL = 'https://api.deepseek.com/chat/completions'
DEEPSEEK_MODEL = 'deepseek-chat'


