import os
from decouple import config
from pathlib import Path
from datetime import timedelta

DEBUG = config('DEBUG', cast=bool)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

BASE_URL = 'http://localhost:8000' if DEBUG else os.getenv("BASE_URL")
CSRF_TRUSTED_ORIGINS=[f"https://*.{BASE_URL}"]
REDIRECT_EMAIL_ACTIVATION = '/api/v2/activation/{}' if DEBUG else '/confirm-confirm/?activation={}'
REDIRECT_TEAM_EMAIL_ACTIVATION = '/api/v2/team/join/{}/{}' if DEBUG else '/dashboard-teams/?tid={}&mid={}'
REDIRECT_EMAIL_CHANGE_PASSWORD = '/newpassword?code={}'
ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True

# Application definition
INSTALLED_APPS = [
    # default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Custom
    'core.apps.CoreConfig',
    'user.apps.UserConfig',
    'tasks.apps.TasksConfig',
    'game.apps.GameConfig',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'tinymce',
    'drf_yasg'
    # 'anymail'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware'
]

ROOT_URLCONF = 'GD.urls'

REST_FRAMEWORK = {
    'DEFAULT_PERMISION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'EXCEPTION_HANDLER': 'GD.custom_exceptions.custom_exception_handler',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )

}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'GD.wsgi.application'

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# TinyMce config
TINYMCE_DEFAULT_CONFIG = {
    "height": "620px",
    "width": "960px",
    "theme": "silver",
    "menubar": "file edit view insert format tools table help",
    "plugins": "advlist autolink lists link image charmap print preview anchor searchreplace visualblocks code "
               "fullscreen insertdatetime media table paste code help wordcount spellchecker",
    "toolbar": "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft "
               "aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor "
               "backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | "
               "fullscreen  preview save print | insertfile image media pageembed template link anchor codesample | "
               "a11ycheck ltr rtl | showcomments addcomment code",
    "custom_undo_redo_levels": 10,
    "language": "fa",  # To force a specific language instead of the Django current language.
    "directionality": "rtl",
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/staticfiles/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static_in_env')]

VENV_PATH = os.path.dirname(BASE_DIR)
MEDIA_URL = os.path.join(BASE_DIR, 'staticfiles/web/media/') if DEBUG else os.path.join('', 'staticfiles/web/media/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'staticfiles/web/media/')

# my custom user model

AUTH_USER_MODEL = 'user.SiteUser'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=10),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=10),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

CELERY_BROKER_URL = os.environ.get(
    'CELERY_BROKER', 'amqp://guest:guest@localhost:5672/')

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# DEBUG PANEL

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]


def show_toolbar(request):
    return DEBUG


DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECT': False,
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
    'IS_RUNNING_TESTS': False
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

PAYWALL = config('PAYWALL')
# idpay settings
X_API_KEY = config('X_API_KEY')
X_SANDBOX = config('X_SANDBOX')
# Payping settings
PAYPING_AUTH = config('PAYPING_AUTH')

# SERVER_EMAIL = 'smtp-relay.sendinblue.com'
# # EMAIL_HOST_USER = config('EMAIL_HOST_USER')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
# EMAIL_PORT = int(config('EMAIL_PORT'))
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
# ANYMAIL = {
#     "SENDINBLUE_API_KEY": config("SENDINBLUE_API_KEY")
# }


DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')
EMAIL_HOST = config("ALT_EMAIL_HOST")
EMAIL_HOST_USER = config("ALT_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("ALT_EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(config("ALT_EMAIL_PORT"))
EMAIL_BACKEND = config("ALT_EMAIL_BACKEND")
EMAIL_TIMEOUT = 10

ALT_EMAIL_HOST = config("ALT_EMAIL_HOST")
ALT_EMAIL_HOST_USER = config("ALT_EMAIL_HOST_USER")
ALT_EMAIL_HOST_PASSWORD = config("ALT_EMAIL_HOST_PASSWORD")
ALT_EMAIL_PORT = int(config("ALT_EMAIL_PORT"))
ALT_EMAIL_BACKEND = config("ALT_EMAIL_BACKEND")

PAYWALL = config('PAYWALL')
PAYPING_AUTH = config("PAYPING_AUTH")
