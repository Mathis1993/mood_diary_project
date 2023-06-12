from clients.forms import ClientCreationForm
from clients.models import Client
from core.views import AuthenticatedCounselorRoleMixin
from diaries.models import MoodDiary
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.views import View

User = get_user_model()


class CreateClientView(AuthenticatedCounselorRoleMixin, View):
    form_class = ClientCreationForm
    template_name = "clients/create_client.html"
    success_template_name = "clients/client_login_details.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            counselor = request.user
            email = form.cleaned_data["email"]
            identifier = form.cleaned_data["identifier"]

            client_user, created = User.objects.get_or_create(email=email, role=User.Role.CLIENT)
            if not created:
                form.add_error("email", ValidationError("client already exists"))
                return render(request, self.template_name, {"form": form})

            password = get_random_string(length=15)
            client_user.set_password(password)
            client_user.save()

            client = Client.objects.create(
                user=client_user, identifier=identifier, counselor=counselor
            )
            MoodDiary.objects.create(client=client)

            return render(
                request, self.success_template_name, {"email": email, "password": password}
            )

        return render(request, self.template_name, {"form": form})
