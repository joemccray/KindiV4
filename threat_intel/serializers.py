from rest_framework import serializers

from .models import Indicator, ThreatReport


class ThreatReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatReport
        fields = ["report_type", "raw_data", "fetched_at"]


class IndicatorSerializer(serializers.ModelSerializer):
    reports = ThreatReportSerializer(many=True, read_only=True)

    class Meta:
        model = Indicator
        fields = [
            "id",
            "value",
            "type",
            "first_seen",
            "last_seen",
            "reports",
        ]
