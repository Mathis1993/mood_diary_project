from core.views import AuthenticatedClientRoleMixin
from diaries.forms import MoodDiaryEntryForm
from diaries.models import MoodDiary, MoodDiaryEntry
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from el_pagination.views import AjaxListView


class RestrictMoodDiaryEntryToOwnerMixin:
    def get_queryset(self):
        return self.model.objects.filter(mood_diary__client_id=self.request.user.client.id)


class MoodDiaryEntryDetailView(
    AuthenticatedClientRoleMixin, RestrictMoodDiaryEntryToOwnerMixin, DetailView
):
    model = MoodDiaryEntry
    template_name = "diaries/mood_diary_entry_get.html"
    context_object_name = "entry"


class MoodDiaryEntryListView(AuthenticatedClientRoleMixin, AjaxListView):
    model = MoodDiaryEntry
    template_name = "diaries/mood_diary_entries_list.html"
    page_template = "diaries/mood_diary_entry_list_page.html"
    context_object_name = "entries"

    def get_queryset(self):
        client_id = self.request.user.client.id
        mood_diary, _ = MoodDiary.objects.get_or_create(client_id=client_id)
        return mood_diary.entries.all().order_by("-date")


class CreateMoodDiaryEntryView(AuthenticatedClientRoleMixin, CreateView):
    model = MoodDiaryEntry
    form_class = MoodDiaryEntryForm
    template_name = "diaries/mood_diary_entry_create.html"

    def form_valid(self, form):
        entry = form.save(commit=False)
        entry.mood_diary = self.request.user.client.mood_diary
        entry.save()
        return redirect("diaries:list_mood_diary_entries")


class MoodDiaryEntryUpdateView(
    AuthenticatedClientRoleMixin, RestrictMoodDiaryEntryToOwnerMixin, UpdateView
):
    model = MoodDiaryEntry
    form_class = MoodDiaryEntryForm
    template_name = "diaries/mood_diary_entry_update.html"

    def get_success_url(self):
        return reverse_lazy("diaries:get_mood_diary_entry", kwargs={"pk": self.object.id})


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
