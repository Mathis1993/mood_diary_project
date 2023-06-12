from diaries.models import MoodDiaryEntry
from django import forms


class MoodDiaryEntryForm(forms.ModelForm):
    class Meta:
        model = MoodDiaryEntry
        fields = [
            "date",
            "start_time",
            "end_time",
            "mood",
            "emotion",
            "mood_and_emotion_info",
            "activity",
            "strain",
            "strain_area",
            "strain_info",
        ]

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
