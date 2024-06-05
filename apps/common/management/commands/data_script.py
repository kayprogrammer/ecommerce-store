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
        }
        reviewer = User.objects.get_or_none(email=user_dict["email"])
        if not reviewer:
            reviewer = User.objects.create_user(**user_dict)
        return reviewer
