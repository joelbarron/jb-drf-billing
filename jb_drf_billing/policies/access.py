class DefaultAccessPolicy:
    def can_check(self, user, *, scope_type: str, profile=None):
        if scope_type == "USER":
            return True
        if scope_type == "PROFILE":
            if profile is None:
                return False
            return getattr(profile, "user_id", None) == getattr(user, "id", None)
        return False
