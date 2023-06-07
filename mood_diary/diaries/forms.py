from diaries.models import MoodDiaryEntry
from django import forms


class MoodDiaryEntryForm(forms.ModelForm):
    class Meta:
        model = MoodDiaryEntry
        fields = [
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
