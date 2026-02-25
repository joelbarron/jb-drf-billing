class BaseCatalogProvider:
    def get_catalog(self, *, user=None, app_slug=None, platform=None, country_code=None, currency=None):
        raise NotImplementedError
