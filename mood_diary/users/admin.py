from typing import Union

from clients.utils import send_account_creation_email
from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.http import HttpRequest, HttpResponse
from django.utils.crypto import get_random_string

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required fields.
    Used in the django admin interface.
    """

    class Meta:
        model = User
        fields = ["email", "role", "is_staff"]


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes some fields on the user model,
    but replaces the password field with a disabled password hash
    display field.
    Used in the django admin interface.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ["email", "password"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Override the base user admin class as much as necessary to work with
    the custom user model in the django admin interface.
    """

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm
    add_form_template = "admin/add_form.html"

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on users.User.
    list_display = ["email", "role", "is_staff", "is_superuser"]
    list_filter = ["is_staff"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "role", "is_staff"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []

    def save_form(
        self, request: HttpRequest, form: Union[UserCreationForm, UserChangeForm], change: bool
    ) -> HttpResponse:
        """
        Send a creation email to a newly created user.
        The admin should only create counselors, so there
        is no further logic executed for other roles.

        Parameters
        ----------
        request: HttpRequest
        form: Union[UserCreationForm, UserChangeForm]
        change: bool
            If true, we deal with a UserChangeForm, otherwise with a UserCreationForm

        Returns
        -------
        HttpResponse
        """
        # Do not execute any further logic on updating a user
        # or if the user is not a counselor.
        user = form.instance
        if change or not user.is_counselor():
            return super().save_form(request, form, change)

        password = get_random_string(length=15)
        user.set_password(password)
        send_account_creation_email(user.email, request.get_host(), request.scheme, password)

        return super().save_form(request, form, change)


# ... And, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
