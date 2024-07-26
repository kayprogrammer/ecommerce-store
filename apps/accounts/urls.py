from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.LoginPageView.as_view(), name="login"),
    path("google/", views.GoogleAuthView.as_view(), name="google-auth"),
    path("facebook/", views.FacebookAuthView.as_view(), name="facebook-auth"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]
