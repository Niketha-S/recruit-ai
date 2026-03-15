from django.urls import path

from . import views

urlpatterns = [
    path("", views.InterviewAnalysis.as_view()),
]