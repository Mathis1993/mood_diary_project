from core.views import AuthenticatedClientRoleMixin, AuthenticatedCounselorRoleMixin
from django.contrib.auth import get_user_model
from django.shortcuts import render
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
                    mood_score_date.strftime("%A")
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
                "mood_highlights": mood_highlights,
            },
        )


class DashboardCounselorView(AuthenticatedCounselorRoleMixin, View):
    template_name = "dashboards/dashboard_counselor.html"

    def get(self, request):
        return render(request, self.template_name, None)
