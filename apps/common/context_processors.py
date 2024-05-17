from django.conf import settings
from apps.general.models import SiteDetail


def sitedetail(request):
    sitedetail, created = SiteDetail.objects.get_or_create()
    sitedetail.google_client_id = settings.GOOGLE_CLIENT_ID
    sitedetail.facebook_app_id = settings.FACEBOOK_APP_ID
    return {"sitedetail": sitedetail}