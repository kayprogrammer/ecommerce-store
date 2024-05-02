from django.conf import settings
from apps.accounts.models import User


class CreateData(object):
    def __init__(self) -> None:
        self.create_superuser()
        self.create_reviewer()

    def create_superuser(self) -> User:
        user_dict = {
            "first_name": "Test",
            "last_name": "Admin",
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
            "is_superuser": True,
            "is_staff": True,
            "is_email_verified": True,
        }
        superuser = User.objects.get_or_none(email=user_dict["email"])
        if not superuser:
            superuser = User.objects.create_user(**user_dict)
        return superuser

    def create_reviewer(self) -> User:
        user_dict = {
            "first_name": "Test",
            "last_name": "Reviewer",
            "email": settings.FIRST_REVIEWER_EMAIL,
            "password": settings.FIRST_REVIEWER_PASSWORD,
            "is_email_verified": True,
        }
        reviewer = User.objects.get_or_none(email=user_dict["email"])
        if not reviewer:
            reviewer = User.objects.create_user(**user_dict)
        return reviewer

    # def create_sitedetail(self) -> SiteDetail:
    #     sitedetail, created = SiteDetail.objects.get_or_create()
    #     return sitedetail
