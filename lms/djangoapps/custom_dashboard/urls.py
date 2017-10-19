from django.conf.urls import url
from custom_dashboard import views

urlpatterns = (
    url(r'^studentsdashboard$', 'views.custom_dashboard', name="custom_dashboard"),
    url(r'^studentfeedback$', 'views.get_feedback', name="studentfeedback"),
)