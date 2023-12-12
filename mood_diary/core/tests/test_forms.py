import pytest
from core.forms import BaseForm, BaseModelForm, FormWithUIClassMixin
from django import forms


def test_form_with_ui_class_mixin():
    class TestForm(FormWithUIClassMixin, forms.Form):
        test_field = forms.CharField()
        another_test_field = forms.IntegerField()

    form = TestForm()

    assert "form-control" in form.fields["test_field"].widget.attrs["class"]
    assert "form-control" in form.fields["another_test_field"].widget.attrs["class"]


def test_base_form_ui_class():
    class TestForm(BaseForm):
        test_field = forms.CharField()

    form = TestForm()
    assert "form-control" in form.fields["test_field"].widget.attrs["class"]


@pytest.mark.django_db
def test_base_model_form_ui_class(django_user_model):
    class UserForm(BaseModelForm):
        class Meta:
            model = django_user_model
            fields = ["email"]

    form = UserForm()
    assert "form-control" in form.fields["email"].widget.attrs["class"]
