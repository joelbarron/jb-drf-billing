SECRET_KEY = "test-secret-key"
DEBUG = True
USE_TZ = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rest_framework",
    "jb_drf_billing",
]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
MIDDLEWARE = []
ROOT_URLCONF = "jb_drf_billing.urls"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
JB_DRF_BILLING = {
    "APP_SLUG": "test-app",
    "BILLING_CUSTOMER_MODEL": "auth.User",
    "PLAN_MODEL": "auth.User",
    "PLAN_PRICE_MODEL": "auth.User",
    "SUBSCRIPTION_MODEL": "auth.User",
    "ENTITLEMENT_MODEL": "auth.User",
    "PLAN_ENTITLEMENT_MODEL": "auth.User",
    "ENTITLEMENT_GRANT_MODEL": "auth.User",
    "BILLING_EVENT_MODEL": "auth.User",
    "CHECKOUT_INTENT_MODEL": "auth.User",
    "PROFILE_MODEL": "auth.User",
}
