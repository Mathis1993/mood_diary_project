from core.forms import BaseModelForm
from diaries.models import Mood, MoodDiaryEntry
from django import forms
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_select2.forms import ModelSelect2Widget


class ActivityWidget(ModelSelect2Widget):
    search_fields = [
        "value_de__icontains",
        "value_en__icontains",
        "category__value_de__icontains",
        "category__value_en__icontains",
    ]
    data_url = reverse_lazy("diaries:mood_diary_entries_create_auto_select")
    max_results = 200

    def __init__(self, *args, **kwargs):
        kwargs["attrs"] = {"data-minimum-input-length": 0}
        super().__init__(*args, **kwargs)


class MoodDiaryEntryForm(BaseModelForm):
    class Meta:
        model = MoodDiaryEntry
        fields = [
            "date",
            "start_time",
            "end_time",
            "activity",
            "mood",
            "details",
        ]
        widgets = {
            "date": forms.DateInput(
                attrs={"placeholder": _("Select a date"), "type": "date"}, format="%Y-%m-%d"
            ),
            "start_time": forms.TimeInput(
                attrs={"placeholder": _("Select a start time"), "type": "time"}, format="%H:%M"
            ),
            "end_time": forms.TimeInput(
                attrs={"placeholder": _("Select an end time"), "type": "time"}, format="%H:%M"
            ),
            "activity": ActivityWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].label = _("Date")
        self.fields["start_time"].label = _("Start time")
        self.fields["end_time"].label = _("End time")
        self.fields["activity"].empty_label = None
        self.fields["activity"].label = _("Activity")
        self.fields["mood"].label = _("Mood")
        self.fields["mood"].empty_label = None
        self.fields["mood"].initial = Mood.objects.get(value=0)
        self.fields["details"].label = _("Details")
        self.fields["details"].widget.attrs.update(
            {
                "rows": 3,
                "placeholder": _("Enter additional details here..."),
                "maxlength": 300,
            }
        )


class MoodDiaryEntryCreateForm(MoodDiaryEntryForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].label = _("Start date")
        self.fields["date"].initial = timezone.now().date().strftime("%Y-%m-%d")
        self.fields["end_date"].initial = timezone.now().date().strftime("%Y-%m-%d")

        now = timezone.now().time()
        self.fields["start_time"].initial = now.strftime("%H:%M")
        self.fields["end_time"].initial = now.strftime("%H:%M")

        self.order_fields(["date", "end_date"])

    end_date = forms.DateField(
        required=False,
        label=_("End date"),
        widget=forms.DateInput(
            attrs={"placeholder": _("Select an end date"), "type": "date"}, format="%Y-%m-%d"
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
