from itertools import groupby

from core.views import AuthenticatedClientRoleMixin
from diaries.forms import MoodDiaryEntryCreateForm, MoodDiaryEntryForm
from diaries.models import Mood, MoodDiary, MoodDiaryEntry
from diaries.tasks import task_event_based_rules_evaluation
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import get_language_from_request
from django.views import View
from django.views.generic import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django_select2.views import AutoResponseView
from el_pagination.views import AjaxListView
from rules.utils import RuleMessage


class RestrictMoodDiaryEntryToOwnerMixin:
    def get_queryset(self):
        return self.model.objects.filter(mood_diary__client_id=self.request.user.client.id)


class MoodDiaryEntryDetailView(
    AuthenticatedClientRoleMixin, RestrictMoodDiaryEntryToOwnerMixin, DetailView
):
    model = MoodDiaryEntry
    template_name = "diaries/mood_diary_entry_get.html"
    context_object_name = "entry"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["moods"] = Mood.objects.all()
        context["label_left"] = Mood.objects.first().label
        context["label_right"] = Mood.objects.last().label
        return context


class MoodDiaryEntryListView(AuthenticatedClientRoleMixin, AjaxListView):
    model = MoodDiaryEntry
    template_name = "diaries/mood_diary_entries_list.html"
    page_template = "diaries/mood_diary_entry_list_page.html"
    context_object_name = "entries"

    def get_queryset(self):
        client_id = self.request.user.client.id
        mood_diary, _ = MoodDiary.objects.get_or_create(client_id=client_id)
        return mood_diary.entries.all()


class MoodDiaryEntryCreateView(AuthenticatedClientRoleMixin, CreateView):
    model = MoodDiaryEntry
    form_class = MoodDiaryEntryCreateForm
    template_name = "diaries/mood_diary_entry_create.html"

    def form_valid(self, form):
        start_time = form.cleaned_data.get("start_time")
        end_time = form.cleaned_data.get("end_time")
        start_date = form.cleaned_data.get("date")
        end_date = form.cleaned_data.get("end_date")
        entry = form.save(commit=False)
        for index in range((days_between := (end_date - start_date).days) + 1):
            entry.id = None
            entry.date = start_date + timezone.timedelta(days=index)
            entry.start_time = "00:00:00"
            entry.end_time = "23:59:59"
            if index == 0:
                entry.start_time = start_time
            if index == days_between:
                entry.end_time = end_time
            entry.mood_diary = (client := self.request.user.client).mood_diary
            entry.save()
            # Trigger evaluation of event-based rules
            msg = RuleMessage(client_id=client.id, timestamp=entry.updated_at)
            task_event_based_rules_evaluation.delay(msg)
        return redirect("diaries:list_mood_diary_entries")


class MoodDiaryEntryUpdateView(
    AuthenticatedClientRoleMixin, RestrictMoodDiaryEntryToOwnerMixin, UpdateView
):
    model = MoodDiaryEntry
    form_class = MoodDiaryEntryForm
    template_name = "diaries/mood_diary_entry_update.html"

    def get_success_url(self):
        return reverse_lazy("diaries:get_mood_diary_entry", kwargs={"pk": self.object.id})

    def form_valid(self, form):
        response = super().form_valid(form)

        # Trigger evaluation of event-based rules
        msg = RuleMessage(client_id=self.request.user.client.id, timestamp=self.object.updated_at)
        task_event_based_rules_evaluation.delay(msg)

        return response


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


class ActivitySelect2QuerySetView(AutoResponseView):
    def get(self, request, *args, **kwargs):
        """
        Django-Select2 does not provide the possibility to combine a search field
        and results organized hierarchically (using <optgroup>) out of the box.
        Therefore, this view processes results for a proper display.
        Return a :class:`.django.http.JsonResponse` with results grouped in a way that
        they can be displayed in <optgroup> options.
        For an example, see https://select2.org/data-sources/formats#grouped-data.
        """
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get("term", request.GET.get("term", ""))
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        result_dict = self.queryset_to_dict(self.object_list)
        result_dict["more"] = context["page_obj"].has_next()
        return JsonResponse(
            result_dict,
            encoder=import_string(settings.SELECT2_JSON_ENCODER),
        )

    def queryset_to_dict(self, queryset):
        """
        Transform the queryset to a dict where activities are ordered within their
        categories.
        Activities are ordered by German categories by default (see the Activity model)
        so that itertool's groupby can work correctly.
        """
        lang = get_language_from_request(self.request)
        if lang == "en":
            queryset = queryset.order_by("category__value_en", "value_en")

        results = []
        for category, activities in groupby(queryset, key=lambda x: x.category):
            category_dict = {
                "text": str(category),
                "children": [{"id": activity.id, "text": str(activity)} for activity in activities],
            }
            results.append(category_dict)

        return {
            "results": results,
        }
