class DefaultFeatureVisibilityPolicy:
    def filter_features(self, features, *, user=None):
        return list(features)
