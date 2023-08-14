from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [
            self.fields[field].widget.attrs.update({"class": "form-control"})
            for field in self.fields.keys()
        ]
