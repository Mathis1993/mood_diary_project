from django import forms


class ClientCreationForm(forms.Form):
    email = forms.EmailField(label="Email")
    identifier = forms.CharField(label="Identifier")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [
            self.fields[field].widget.attrs.update({"class": "form-control"})
            for field in self.fields.keys()
        ]
