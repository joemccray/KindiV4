from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Indicator, ThreatReport


class ThreatIntelModelsTest(TestCase):
    def test_create_indicator(self):
        indicator = Indicator.objects.create(
            value="example.com", type=Indicator.IndicatorType.DOMAIN
        )
        self.assertEqual(str(indicator), "Domain: example.com")
        self.assertEqual(Indicator.objects.count(), 1)

    def test_create_threat_report(self):
        indicator = Indicator.objects.create(
            value="example.com", type=Indicator.IndicatorType.DOMAIN
        )
        report = ThreatReport.objects.create(
            indicator=indicator,
            report_type="passive_dns",
            raw_data={"results": ["1.1.1.1"]},
        )
        self.assertEqual(report.indicator, indicator)
        self.assertEqual(ThreatReport.objects.count(), 1)
        self.assertEqual(str(report), "passive_dns for example.com")


class ThreatIntelApiTest(APITestCase):
    @patch("threat_intel.views.services.get_domain_intel")
    def test_domain_lookup_api(self, mock_get_domain_intel):
        # Configure the mock to return a predictable Indicator object
        indicator = Indicator(value="test.com", type=Indicator.IndicatorType.DOMAIN)
        mock_get_domain_intel.return_value = indicator

        url = reverse("threatintel-domain-lookup", kwargs={"domain_name": "test.com"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_domain_intel.assert_called_once_with("test.com")
        self.assertEqual(response.data["value"], "test.com")

    @patch("threat_intel.views.services.get_ip_intel")
    def test_ip_lookup_api(self, mock_get_ip_intel):
        indicator = Indicator(value="1.2.3.4", type=Indicator.IndicatorType.IPV4)
        mock_get_ip_intel.return_value = indicator

        url = reverse("threatintel-ip-lookup", kwargs={"ip_address": "1.2.3.4"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_ip_intel.assert_called_once_with("1.2.3.4")
        self.assertEqual(response.data["value"], "1.2.3.4")

    @patch("threat_intel.views.services.get_hash_intel")
    def test_hash_lookup_api(self, mock_get_hash_intel):
        file_hash = "a" * 32  # MD5
        indicator = Indicator(value=file_hash, type=Indicator.IndicatorType.MD5)
        mock_get_hash_intel.return_value = indicator

        url = reverse("threatintel-hash-lookup", kwargs={"file_hash": file_hash})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_hash_intel.assert_called_once_with(file_hash)
        self.assertEqual(response.data["value"], file_hash)
