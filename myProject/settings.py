from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*=hdmmg^5%92(1atrd%u9avi_g^qvx+uj$z)$0*otz4_8=o3xp'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# settings.py
# --- existing ---
ALLOWED_HOSTS = [
    "*",
    "industryrockstar-production.up.railway.app",
    "www.industryrockstar-production.up.railway.app",
    "solutionsforchange.org",
    "www.solutionsforchange.org",
    "juliaportfolio-production.up.railway.app",
    "www.juliaportfolio-production.up.railway.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://industryrockstar-production.up.railway.app",
    "https://www.industryrockstar-production.up.railway.app",
    # Optional (safe): include partner if you ever use absolute POST URLs or JS fetches from their domain
    "https://solutionsforchange.org",
    "https://www.solutionsforchange.org",
    "https://juliaportfolio-production.up.railway.app",
    "https://www.juliaportfolio-production.up.railway.app",
]

X_FRAME_OPTIONS = "ALLOWALL"

CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True




# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myApp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'myApp.middleware.FrameAncestorsMiddleware',
]

ROOT_URLCONF = 'myProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'myProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


import os

# Stripe Configuration - Load from environment variables (loaded via dotenv at top of file)
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Validate that Stripe keys are set
if not STRIPE_SECRET_KEY:
    import warnings
    warnings.warn(
        "STRIPE_SECRET_KEY is not set in environment variables. "
        "Please add it to your .env file: STRIPE_SECRET_KEY=sk_test_... or STRIPE_SECRET_KEY=sk_live_..."
    )
DOMAIN = os.environ.get("DOMAIN", "http://localhost:8000")

# Base Network / USDC Configuration
CHAIN = os.environ.get("CHAIN", "base")
BASE_RPC_URL = os.environ.get("BASE_RPC_URL", "")  # From Alchemy (SECRET - must be set)
RECEIVER_WALLET = os.environ.get("RECEIVER_WALLET", "0x918e03d7c59d61b6505fed486082419941ffd77f")
USDC_CONTRACT_ADDRESS = os.environ.get("USDC_CONTRACT_ADDRESS", "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913")
USDC_DECIMALS = int(os.environ.get("USDC_DECIMALS", "6"))
REQUIRED_CONFIRMATIONS = int(os.environ.get("REQUIRED_CONFIRMATIONS", "2"))

# Webhook Configuration
PAYMENT_WEBHOOK_URL = os.environ.get("PAYMENT_WEBHOOK_URL", "https://services.leadconnectorhq.com/hooks/QHdTN3veuJ2AYB8f9dQt/webhook-trigger/ca7e5231-a2af-4f8b-8d0c-59ea1a9d364f")