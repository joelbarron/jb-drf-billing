from django.apps import AppConfig


class JbDrfBillingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jb_drf_billing"
    verbose_name = "JB DRF Billing"

    def ready(self):
        from jb_drf_billing import checks  # noqa: F401
