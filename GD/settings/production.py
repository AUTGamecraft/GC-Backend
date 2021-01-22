from .base import * 


DEBUG = config('DEBUG' , cast=bool )

ALLOWED_HOSTS = ['*']



# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('POSTGRES_USER'),
        'USER': config('POSTGRES_USER'),
        'PASSWORD' : config('POSTGRES_PASSWORD'),
        'HOST' : config('POSTGRES_HOST'),
        'PORT' : config('POSTGRES_PORT')
    }
}


STRIPE_PUBLIC_KEY = ''
STRIPE_SECRET_KEY = '' 