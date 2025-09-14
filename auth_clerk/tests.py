from django.test import RequestFactory, TestCase

from .drf_auth import ClerkAuthentication


class TestClerkAuth(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_missing_token_is_anon(self):
        req = self.factory.get("/whoami")
        auth = ClerkAuthentication()
        assert auth.authenticate(req) is None  # DRF will treat as no credentials

    def test_auth_header_format(self):
        req = self.factory.get("/whoami", HTTP_AUTHORIZATION="Bearer ")
        auth = ClerkAuthentication()
        try:
            auth.authenticate(req)
        except Exception as e:
            assert "Invalid token header" in str(e)
