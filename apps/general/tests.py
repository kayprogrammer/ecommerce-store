from django.test import TestCase
from django.conf import settings
from django.urls import reverse

from apps.common.utils import TestUtil
from apps.general.forms import MessageForm

settings.TESTING = True


class TestGeneral(TestCase):
    home_url = reverse("home")
    contact_url = reverse("contact")

    def setUp(self):
        user = TestUtil.new_user()
        product = TestUtil.create_product()
        self.product = product

    def test_home(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["products"], [self.product])

    def test_subscribe(self):
        # Check response validity
        response = self.client.post(
            self.home_url, {"email": "test_subscriber@example.com"}
        )
        self.assertRedirects(
            response,
            "/",
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_contact(self):
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], MessageForm)

        # POST
        response = self.client.post(
            self.contact_url,
            {
                "name": "Test Contacter",
                "email": "test_contacter@example.com",
                "subject": "Whatever it is",
                "text": "Whatever this is about man",
            },
        )
        self.assertRedirects(
            response,
            self.contact_url,
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )
