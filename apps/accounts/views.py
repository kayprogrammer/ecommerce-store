from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import LogoutRequiredMixin
from .auth import Facebook, Google, register_social_user

# Create your views here.


class LoginPageView(LogoutRequiredMixin, View):
    def get(self, request):
        context = {}
        return render(request, "accounts/login.html", context=context)


class GoogleAuthView(LogoutRequiredMixin, View):
    def get(self, request):
        auth_token = request.GET.get("auth_token")
        user_data = Google.validate(auth_token)
        try:
            user_data["sub"]
        except:
            # Invalid auth token
            return redirect("/")
        if user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            # Invalid client id
            return redirect("/")
        user = register_social_user(
            request, user_data["email"], user_data["name"], user_data["picture"]
        )
        login(request, user)
        return redirect("/")


class FacebookAuthView(LogoutRequiredMixin, View):
    def get(self, request):
        auth_token = request.GET.get("auth_token")
        user_data = Facebook.validate(auth_token)
        user = register_social_user(request, user_data["email"], user_data["name"])
        login(request, user)
        return redirect("/")


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect("/")
