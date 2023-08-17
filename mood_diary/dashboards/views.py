from core.views import AuthenticatedClientRoleMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.views import View

User = get_user_model()


class DashboardClientView(AuthenticatedClientRoleMixin, View):
    template_name = "dashboards/dashboard_client.html"

    def get(self, request):
        user = request.user
        mood_diary = user.client.mood_diary
        mood_scores = mood_diary.average_mood_scores_previous_days(7)
        mood_scores_dates = list(
            reversed(
                [
                    _(mood_score_date.strftime("%A"))
                    for mood_score_date in mood_scores.values_list("date", flat=True)
                ]
            )
        )
        mood_scores_values = list(
            reversed(
                [
                    round(mood_score_value, 1)
                    for mood_score_value in mood_scores.values_list("average_mood", flat=True)
                ]
            )
        )
        mood_highlights = mood_diary.most_recent_mood_highlights(3)
        return render(
            request,
            self.template_name,
            {
                "mood_scores_values": mood_scores_values,
                "mood_scores_dates": mood_scores_dates,
                "mood_score_data_name": _("Average Mood"),
                "mood_highlights": mood_highlights,
                "ask_for_push_notifications_permission": user.client.ask_for_push_notifications_permission(),  # noqa E501
                "vapid_public_key": settings.VAPID_PUBLIC_KEY,
            },
        )
