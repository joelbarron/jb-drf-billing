from rest_framework.permissions import IsAuthenticated


class BillingAuthenticated(IsAuthenticated):
    pass
