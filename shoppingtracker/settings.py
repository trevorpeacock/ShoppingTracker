DATA_PATH = './data/'

# API Key from eandata.com
EANDATA_KEY = ''

# API Key from digit-eyes.com
DIGITEYES_AUTH_KEY = ''
DIGITEYES_APP_KEY = ''

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path('~/.shoppingtracker/').expanduser()
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '***UnusedSecret***'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition
INSTALLED_APPS = [
    'shoppingtracker.db',
]


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR / 'db.sqlite3',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

