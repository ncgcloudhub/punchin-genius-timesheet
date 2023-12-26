# /time_tracker/settings.py --> project settings


"""
Django settings for time_tracker project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-0(i)s^cs77ka$g_@2jp%6@qtj8+h5kx(=figl1vch2uja7^40i"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",
    "employer",
    "crispy_forms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "time_tracker.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.tz",
            ],
        },
    },
]

WSGI_APPLICATION = "time_tracker.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'timetracker_db',
        'USER': 'postgres',
        'PASSWORD': 'pass23!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Custom User Model (not using the django user model).  The line below pointing to custom user model.
AUTH_USER_MODEL = 'core.PunchinUser'

# LOGIN_REDIRECT_URL set to the 'dashboard' URL. This tells Django where to redirect after a successful login
LOGIN_URL = 'login'
# or wherever you want to redirect users after login
# LOGIN_REDIRECT_URL = 'dashboard'
# The URL name for the view that decides where to redirect users after login
LOGIN_REDIRECT_URL = 'dashboard_redirect'


# ensure cookies are only sent over HTTPS.
SESSION_COOKIE_SECURE = True

# configure the email backend (example with console backend for development):
# For development only.
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# settings.py (development settings)
MY_DOMAIN = 'http://localhost:8000'

# Production
# MY_DOMAIN = '# settings.py (production settings)
# MY_DOMAIN = 'https://punchin.stritstax.com'


# For production, you will need to configure a real email backend. For production, use SMTP backend.  See https://docs.djangoproject.com/en/4.2/topics/email/#smtp-backend

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'trionxai@gmail.com'
EMAIL_HOST_PASSWORD = 'sdfsdfwer21'


# Email template settings
PASSWORD_RESET_EMAIL_TEMPLATE_NAME = 'registration/password_reset_email.html'
PASSWORD_RESET_SUBJECT_TEMPLATE_NAME = 'registration/password_reset_subject.txt'


# Create a 'logs' directory in your project folder
LOGGING_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGGING_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',  # Set the logging level to DEBUG
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGGING_DIR, 'debug.log'),
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',  # Set the root logger level to DEBUG
    },
}