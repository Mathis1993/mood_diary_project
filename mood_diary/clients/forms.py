from core.forms import BaseForm
from django import forms


class ClientCreationForm(BaseForm):
    email = forms.EmailField(label="Email")
    identifier = forms.CharField(label="Identifier")
