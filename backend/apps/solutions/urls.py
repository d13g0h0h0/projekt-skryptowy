from django.urls import path

from . import views

urlpatterns = [
    path("tasks/<int:task_pk>/solutions/", views.SolutionListView.as_view()),
    path("solutions/<int:pk>/", views.SolutionDetailView.as_view()),
    path("solutions/<int:solution_pk>/vote/", views.SolutionVoteView.as_view()),
]