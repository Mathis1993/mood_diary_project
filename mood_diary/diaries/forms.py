from diaries.models import Mood, MoodDiaryEntry
from django import forms


class MoodDiaryEntryForm(forms.ModelForm):
    class Meta:
        model = MoodDiaryEntry
        fields = [
            "date",
            "start_time",
            "end_time",
            "activity",
            "mood",
            "mood_and_emotion_info",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={"placeholder": "Select a date", "type": "date"},
            ),
            "start_time": forms.TimeInput(
                attrs={"placeholder": "Select a start time", "type": "time"},
            ),
            "end_time": forms.TimeInput(
                attrs={"placeholder": "Select an end time", "type": "time"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [
            self.fields[field].widget.attrs.update({"class": "form-control"})
            for field in self.fields.keys()
        ]
        self.fields["activity"].empty_label = None
        self.fields["mood"].empty_label = None
        self.fields["mood"].initial = Mood.objects.get(value=0)
        self.fields["mood_and_emotion_info"].widget.attrs.update(
            {"rows": 5, "placeholder": "Enter any additional info here"}
        )

    def clean(self):
        cleaned_data = super().clean()
        strain = cleaned_data.get("strain")
        if strain:
            return cleaned_data

        strain_area = cleaned_data.get("strain_area")
        if strain_area:
            self.add_error("strain_area", "Please set a strain when choosing a strain area.")

        strain_info = cleaned_data.get("strain_info")
        if strain_info:
            self.add_error("strain_info", "Please set a strain when providing strain info.")
