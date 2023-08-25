from clients.forms import ClientCreationForm
from clients.models import Client
from core.utils import send_account_creation_email
from core.views import AuthenticatedCounselorRoleMixin
from diaries.models import Mood, MoodDiary, MoodDiaryEntry
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView
from el_pagination.views import AjaxListView
from rules.models import Rule

User = get_user_model()


class RestrictToOwnClientsAndReleasedEntriesMixin:
    def get_queryset(self):
        client_id = self.kwargs.get(self.pk_client_kwarg)
        mood_diary, _ = MoodDiary.objects.get_or_create(
            client_id=client_id,
            client__counselor_id=self.request.user.id,
        )
        return mood_diary.entries.filter(released=True)


class CreateClientView(AuthenticatedCounselorRoleMixin, View):
    form_class = ClientCreationForm
    template_name = "clients/client_create.html"
    success_template_name = "clients/client_creation_success.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            counselor = request.user
            email = form.cleaned_data["email"]
            identifier = form.cleaned_data["identifier"]
            password = get_random_string(length=15)

            client_user, created = User.objects.get_or_create(email=email, role=User.Role.CLIENT)
            if not created:
                form.add_error("email", ValidationError(_("Client already exists")))
                return render(request, self.template_name, {"form": form})

            try:
                send_account_creation_email(email, request.get_host(), request.scheme, password)
            except Exception:
                form.add_error("email", ValidationError(_("Could not send email")))
                client_user.delete()
                return render(request, self.template_name, {"form": form})

            client_user.set_password(password)
            client_user.save()

            client = Client.objects.create(
                user=client_user, identifier=identifier, counselor=counselor
            )
            MoodDiary.objects.create(client=client)
            client.subscribed_rules.add(*Rule.objects.all())

            return render(request, self.success_template_name, {"email": email})

        return render(request, self.template_name, {"form": form})


class ClientListView(AuthenticatedCounselorRoleMixin, AjaxListView):
    model = Client
    template_name = "clients/clients_list.html"
    page_template = "clients/clients_list_page.html"
    context_object_name = "clients"

    def get_queryset(self):
        counselor_id = self.request.user.id
        return Client.objects.filter(counselor_id=counselor_id, active=True).order_by("-created_at")


class ClientUpdateToInactiveView(AuthenticatedCounselorRoleMixin, View):
    def post(self, request, pk):
        client = Client.objects.get(id=pk)
        counselor_id = self.request.user.id
        if client.counselor_id == counselor_id:
            client.active = False
            client.save()
        return redirect(reverse_lazy("clients:list_clients"))


class MoodDiaryEntryListCounselorView(
    AuthenticatedCounselorRoleMixin, RestrictToOwnClientsAndReleasedEntriesMixin, AjaxListView
):
    model = MoodDiaryEntry
    template_name = "clients/mood_diary_entries_list.html"
    page_template = "clients/mood_diary_entries_list_page.html"
    context_object_name = "entries"
    pk_client_kwarg = "client_pk"


class MoodDiaryEntryDetailView(
    AuthenticatedCounselorRoleMixin, RestrictToOwnClientsAndReleasedEntriesMixin, DetailView
):
    model = MoodDiaryEntry
    template_name = "clients/mood_diary_entry_get.html"
    context_object_name = "entry"
    pk_client_kwarg = "client_pk"
    pk_url_kwarg = "entry_pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["moods"] = Mood.objects.all()
        context["label_left"] = Mood.objects.first().label
        context["label_right"] = Mood.objects.last().label
        return context
