from datetime import date

from core.forms import GroupedModelChoiceField
from diaries.models import Activity, Mood, MoodDiaryEntry
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

    activity = GroupedModelChoiceField(queryset=Activity.objects.all(), choices_group_by="category")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [
            self.fields[field].widget.attrs.update({"class": "form-control"})
            for field in self.fields.keys()
        ]
        self.fields["activity"].empty_label = None
        self.fields["mood"].empty_label = None
        self.fields["mood"].initial = Mood.objects.get(value=0)
        self.fields["mood_and_emotion_info"].label = "Additional info"
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

        return cleaned_data


class MoodDiaryEntryCreateForm(MoodDiaryEntryForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].label = "Start date"
        self.order_fields(["date", "end_date"])

    end_date = forms.DateField(
        initial=date.today(),
        required=False,
        widget=forms.DateInput(
            attrs={"placeholder": "Select an end date", "type": "date"},
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get("end_date"):
            cleaned_data["end_date"] = cleaned_data.get("date")

        start_date = cleaned_data.get("date")
        end_date = cleaned_data.get("end_date")
        if start_date and end_date:
            if start_date > end_date:
                self.add_error("end_date", "End date must be after start date.")

        return cleaned_data
