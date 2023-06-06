from django import forms


class ClientCreationForm(forms.Form):
    email = forms.EmailField(label="Email")
    identifier = forms.CharField(label="Identifier")
