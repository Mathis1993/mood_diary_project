from core.views import AuthenticatedClientRoleMixin
from diaries.forms import MoodDiaryEntryForm
from diaries.models import MoodDiary, MoodDiaryEntry
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, ListView, UpdateView
from django.views.generic.detail import DetailView


class RestrictMoodDiaryEntryToOwnerMixin:
    def get_queryset(self):
        return self.model.objects.filter(mood_diary__client_id=self.request.user.client.id)


class MoodDiaryEntryDetailView(
    AuthenticatedClientRoleMixin, RestrictMoodDiaryEntryToOwnerMixin, DetailView
):
    model = MoodDiaryEntry
    template_name = "diaries/mood_diary_entry_get.html"
    context_object_name = "entry"


class MoodDiaryEntryListView(AuthenticatedClientRoleMixin, ListView):
    model = MoodDiaryEntry
    template_name = "diaries/mood_diary_entries_list.html"
    context_object_name = "entries"
    paginate_by = 10

    def get_queryset(self):
        client_id = self.request.user.client.id
        mood_diary, _ = MoodDiary.objects.get_or_create(client_id=client_id)
        return mood_diary.entries.all().order_by("-date")


class CreateMoodDiaryEntryView(AuthenticatedClientRoleMixin, View):
    form_class = MoodDiaryEntryForm
    template_name = "diaries/mood_diary_entry_create.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.mood_diary = request.user.client.mood_diary
            entry.save()
            return redirect("diaries:list_mood_diary_entries")
        return render(request, self.template_name, {"form": form})


class MoodDiaryEntryUpdateView(
    AuthenticatedClientRoleMixin, RestrictMoodDiaryEntryToOwnerMixin, UpdateView
):
    model = MoodDiaryEntry
    template_name = "diaries/mood_diary_entry_update.html"
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
    success_url = reverse_lazy("diaries:list_mood_diary_entries")


class MoodDiaryEntryDeleteView(
    AuthenticatedClientRoleMixin, RestrictMoodDiaryEntryToOwnerMixin, DeleteView
):
    model = MoodDiaryEntry
    template_name = "diaries/mood_diary_entry_delete.html"
    context_object_name = "entry"
    success_url = reverse_lazy("diaries:list_mood_diary_entries")


class MoodDiaryEntryReleaseView(AuthenticatedClientRoleMixin, View):
    template_name = "diaries/mood_diary_entry_release.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        mood_diary = self.request.user.client.mood_diary
        mood_diary.release_entries()
        return redirect("diaries:release_mood_diary_entries_done")


class MoodDiaryEntryReleaseDoneView(AuthenticatedClientRoleMixin, View):
    template_name = "diaries/mood_diary_entry_release_done.html"

    def get(self, request):
        return render(request, self.template_name)
