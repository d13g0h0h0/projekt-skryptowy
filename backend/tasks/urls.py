from django.urls import path
from . import views

urlpatterns = [
    path("", views.TaskListView.as_view()),
    path("<int:pk>/", views.TaskDetailView.as_view()),
]