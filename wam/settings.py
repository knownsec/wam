#!/usr/bin/env python
# coding: utf8

"""
Django settings for wam project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.conf import global_settings


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATE_DIRS = (BASE_DIR + '/wam/templates',)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jk&z8&k*z#=25f7$e!o@^#^y8)a-373!#0eye^fm24s7lu^m@m'
# SECRET_KEY = os.urandom(64)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

SESSION_COOKIE_AGE = 60*60*24
SESSION_COOKIE_NAME = 'wam_sessionid'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

INSTALLED_APPS += (
    'wam.apps.am',
    'wam.apps.fm',
    'wam.apps.main',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'wam.urls'

WSGI_APPLICATION = 'wam.wsgi.application'

AUTHENTICATION_BACKENDS = (
    #'wam.ldap_backend.LDAPBackend', # 如果想使用 LDAP 认证取消注释
    'django.contrib.auth.backends.ModelBackend',
)

LDAP_SERVER_DOMAIN = 'test.com'
LDAP_SERVER_URI = 'ldaps://ldap.test.com'
LDAP_USER_DN_TEMPLATE = 'uid=%s,ou=People,dc=test,dc=com'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
# dev
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# production
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'wamdb',
#         'USER': 'root',
#         'PASSWORD': 'password',
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#     }
# }


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh-CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'wam/static'),
)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


PACKAGE_SOTRE_DIR = os.path.join(BASE_DIR, 'wam/packages/')
FILE_STORE_DIR = os.path.join(BASE_DIR, 'wam/files/')


WAM_VENDOR_LOGO_URL = '/static/images/logo/'
WAM_VENDOR_LOGO_ROOT = os.path.join(BASE_DIR, 'wam/static/images/logo')

# Email Settings
EMAIL_HOST = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
