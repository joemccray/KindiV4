from unittest.mock import patch

from django.contrib.auth.models import User
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
    @patch("threat_intel.services.task_get_domain_intel.delay")
    def test_get_domain_intel_triggers_task(self, mock_delay):
        domain = "example.com"
        services.get_domain_intel(domain)
        # Check that an indicator is created immediately
        self.assertTrue(Indicator.objects.filter(value=domain).exists())
        # Check that the Celery task was called
        mock_delay.assert_called_once_with(domain)

    @patch("threat_intel.services.task_get_ip_intel.delay")
    def test_get_ip_intel_triggers_task(self, mock_delay):
        ip = "8.8.8.8"
        services.get_ip_intel(ip)
        self.assertTrue(Indicator.objects.filter(value=ip).exists())
        mock_delay.assert_called_once_with(ip)

    @patch("threat_intel.services.task_get_hash_intel.delay")
    def test_get_hash_intel_triggers_task(self, mock_delay):
        file_hash = "a" * 32
        services.get_hash_intel(file_hash)
        self.assertTrue(Indicator.objects.filter(value=file_hash).exists())
        mock_delay.assert_called_once_with(file_hash)


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
