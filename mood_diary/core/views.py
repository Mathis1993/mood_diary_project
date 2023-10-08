from django.contrib.auth.mixins import AccessMixin
from django.http import HttpRequest


class AuthenticatedCounselorRoleMixin(AccessMixin):
    """
    Mixin to restrict access to counselor users.
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not (user := request.user).is_authenticated or not user.is_counselor():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AuthenticatedClientRoleMixin(AccessMixin):
    """
    Mixin to restrict access to client users.
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not (user := request.user).is_authenticated or not user.is_client():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AuthenticatedCounselorOrClientRoleMixin(AccessMixin):
    """
    Mixin to restrict access to counselor or client users
    (so to authenticated users, essentially).
    """

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not (user := request.user).is_authenticated or not (
            user.is_counselor() or user.is_client()
        ):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
