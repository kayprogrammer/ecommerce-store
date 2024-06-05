from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.general.urls")),
    path("admin/", admin.site.urls),
]
