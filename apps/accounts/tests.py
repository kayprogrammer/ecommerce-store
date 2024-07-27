from django.test import TestCase
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from apps.common.utils import TestUtil

settings.TESTING = True

token_generator = PasswordResetTokenGenerator()


class TestAccounts(TestCase):
    login_url = "/accounts/login/"
    logout_url = "/accounts/logout/"

    def setUp(self):
        self.new_user = TestUtil.new_user()

    def test_login(self):
        # GET #
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_logout(self):
        verified_user = self.new_user

        # Ensures A user logs out successfully
        self.client.login(email=verified_user.email, password="testpassword")
        response = self.client.get(self.logout_url)
        self.assertRedirects(
            response,
            "/",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    # No be me go do everything. Write tests for google and facebook auth yourself. I don tire.
