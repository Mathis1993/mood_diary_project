from django.contrib.auth.mixins import AccessMixin


class AuthenticatedCounselorRoleMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not (user := request.user).is_authenticated or not user.is_counselor():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AuthenticatedClientRoleMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not (user := request.user).is_authenticated or not user.is_client():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
