from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from .auth import ScopedTokenSerializer
from .views import RegisterView

urlpatterns = [
    # sesja (frontend)
    path("login/", views.LoginView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("me/", views.MeView.as_view()),
    path("register/", RegisterView.as_view()),
    # JWT (inni klienci)
    path("token/", TokenObtainPairView.as_view(serializer_class=ScopedTokenSerializer)),
    path("token/refresh/", TokenRefreshView.as_view()),
]