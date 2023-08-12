from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_account_creation_email(to_email: str, host: str, scheme: str, initial_password: str):
    """
    Sends an email to the client with the initial password.
    A html message is sent if the email client supports it, otherwise a fallback message is sent.
    """
    url = f"{scheme}://{host}"
    fallback_message = f"""
Hallo!

Deine Emailadresse wurde für eine Registrierung für das Mood Diary verwendet.

Wenn das korrekt ist, logge dich bitte mit dieser Emailadresse und dem unten stehenden Passwort
auf {url} ein.
Du wirst dann aufgefordert, ein eigenes Passwort zu setzen.

Danke, dass Du das Mood Diary nutzt!

Zugangspasswort: {initial_password}

*** ENGLISH VERSION ***

Hello!

Your email address has been used to register for the Mood Diary.

If that is correct, please use this email address and the password below to log in at  {url}.
You will be prompted to create your own password.

Thank you for using the Mood Diary!

Initial password: {initial_password}
"""
    context = {
        "host": host,
        "url": url,
        "password": initial_password,
    }
    html_content = render_to_string("users/registration_email.html", context)
    send_mail(
        "Registration for the Mood Diary",
        fallback_message,
        settings.FROM_EMAIL,
        [to_email],
        fail_silently=False,
        html_message=html_content,
    )
