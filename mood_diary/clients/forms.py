from core.forms import BaseForm
from django import forms


class ClientCreationForm(BaseForm):
    """
    Form for creating a new client.
    """

    email = forms.EmailField(label="Email")
    identifier = forms.CharField(label="Identifier")
