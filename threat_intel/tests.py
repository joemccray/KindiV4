from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import services
from .models import Indicator, ThreatReport


class ThreatIntelModelsTest(TestCase):
    def test_create_indicator(self):
        indicator = Indicator.objects.create(
            value="example.com", type=Indicator.IndicatorType.DOMAIN
        )
        self.assertEqual(str(indicator), "Domain: example.com")

    def test_create_threat_report(self):
        indicator = Indicator.objects.create(
            value="example.com", type=Indicator.IndicatorType.DOMAIN
        )
        report = ThreatReport.objects.create(
            indicator=indicator,
            report_type="passive_dns",
            raw_data={"results": ["1.1.1.1"]},
        )
        self.assertEqual(str(report), "passive_dns for example.com")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class ThreatIntelServiceTest(TestCase):
    def tearDown(self):
        cache.clear()

    @patch("threat_intel.services.get_rotated_session")
    def test_get_domain_intel_service(self, mock_get_session):
        # Setup Mocks
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status_code": "200",
            "results": [{"domain": "sub.example.com"}],
        }
        mock_session.get.return_value = mock_response

        # Action
        indicator = services.get_domain_intel("example.com")

        # Assertions
        self.assertEqual(indicator.value, "example.com")
        self.assertEqual(indicator.reports.count(), 5)  # 5 report types for domains

        report = indicator.reports.get(report_type="subdomains")
        self.assertEqual(report.raw_data[0]["domain"], "sub.example.com")

        # Verify rate limit was checked 5 times
        self.assertEqual(mock_session.get.call_count, 5)

    @patch("threat_intel.services.get_rotated_session")
    def test_rate_limiting(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Manually exhaust the rate limit
        for _ in range(services.RATE_LIMIT_COUNT):
            self.assertTrue(services._check_rate_limit())

        # This call should now be blocked
        self.assertFalse(services._check_rate_limit())

        # Action: Call the service function for a new indicator
        indicator = services.get_domain_intel("rate-limited-domain.com")

        # Assertions: No API calls should have been made
        mock_session.get.assert_not_called()

        # The indicator is created, but no reports are fetched for it
        self.assertEqual(indicator.reports.count(), 0)
        self.assertTrue(
            Indicator.objects.filter(value="rate-limited-domain.com").exists()
        )


class ThreatIntelApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)

    @patch("threat_intel.views.services.get_domain_intel")
    def test_domain_lookup_api(self, mock_get_domain_intel):
        cve_id = "test.com"
        # The service returns an indicator with related reports, which the serializer will handle
        indicator = Indicator.objects.create(
            value=cve_id, type=Indicator.IndicatorType.DOMAIN
        )
        ThreatReport.objects.create(
            indicator=indicator, report_type="whois", raw_data={}
        )
        mock_get_domain_intel.return_value = indicator

        url = reverse("threatintel-domain-lookup", kwargs={"domain_name": cve_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_domain_intel.assert_called_once_with(cve_id)
        self.assertEqual(response.data["value"], cve_id)
        self.assertEqual(len(response.data["reports"]), 1)
