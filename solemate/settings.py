"""
Django settings for the SoleMate project.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / "ai.env")
BASE_DIR = Path(__file__).resolve().parent.parent
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
SECRET_KEY = 'django-insecure-CHANGE-ME-before-deploying'
DEBUG = False

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'store',
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

ROOT_URLCONF = 'solemate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Project-level templates dir (not required since each app has
        # its own templates/ folder too, but handy for shared templates).
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'solemate.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'store' / 'static']

# Uploaded files (e.g. product photos added in the admin) live here.
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


RAZORPAY_KEY_ID = 'rzp_test_TXZmC54IbH8ksa'
RAZORPAY_KEY_SECRET = 'RnMUpOmlDNLJe2o2BQkTveMO'


GEMINI_API_KEY = 'AQ.Ab8RN6Lhvam7GdZf6z1oTIoJfRANLsH_Y-WXE7qry_Vj33qcUA'
GEMINI_MODEL = 'gemini-2.5-flash'



EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ---- Auth-related redirects used by the login page ----
LOGIN_URL = 'login'                 # name of the login URL pattern
LOGIN_REDIRECT_URL = 'home'         # where to send users after a successful login
LOGOUT_REDIRECT_URL = 'home'        # where to send users after logout
import os
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')