from datetime import date

from diaries.models import Mood, MoodDiaryEntry
from django import forms
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget


# ToDo(ME-14.08.23): Test
class ActivityWidget(ModelSelect2Widget):
    search_fields = [
        "value_de__icontains",
        "value_en__icontains",
        "category__value_de__icontains",
        "category__value_en__icontains",
    ]
    data_url = reverse_lazy("diaries:mood_diary_entries_create_auto_select")

    def __init__(self, *args, **kwargs):
        kwargs["attrs"] = {"data-minimum-input-length": 0}
        super().__init__(*args, **kwargs)


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
                attrs={"placeholder": _("Select a date"), "type": "date"},
            ),
            "start_time": forms.TimeInput(
                attrs={"placeholder": _("Select a start time"), "type": "time"},
            ),
            "end_time": forms.TimeInput(
                attrs={"placeholder": _("Select an end time"), "type": "time"},
            ),
            "activity": ActivityWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        [
            self.fields[field].widget.attrs.update({"class": "form-control"})
            for field in self.fields.keys()
        ]
        self.fields["date"].label = _("Date")
        self.fields["start_time"].label = _("Start time")
        self.fields["end_time"].label = _("End time")
        self.fields["activity"].empty_label = None
        self.fields["mood"].label = _("Mood")
        self.fields["mood"].empty_label = None
        self.fields["mood"].initial = Mood.objects.get(value=0)
        self.fields["mood_and_emotion_info"].label = _("Additional info")
        self.fields["mood_and_emotion_info"].widget.attrs.update(
            {"rows": 5, "placeholder": _("Enter any additional info here")}
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
        self.fields["date"].label = _("Start date")
        # self.fields["end_date"].initial = timezone.now().date()
        # self.fields["start_time"].initial = timezone.now()
        # self.fields["end_time"].initial = timezone.now()

        # ToDo(ME-13.08.23): Handle initial value for date fields
        now = timezone.now().time()
        self.fields["start_time"].initial = now.strftime("%H:%M")
        self.fields["end_time"].initial = now.strftime("%H:%M")

        self.order_fields(["date", "end_date"])

    end_date = forms.DateField(
        initial=date.today,
        required=False,
        label=_("End date"),
        widget=forms.DateInput(
            attrs={"placeholder": _("Select an end date"), "type": "date"},
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
                self.add_error("end_date", _("End date must be after start date."))

        return cleaned_data
