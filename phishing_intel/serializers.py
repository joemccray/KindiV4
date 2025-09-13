from rest_framework import serializers

from .models import URLCheck


class URLCheckRequestSerializer(serializers.Serializer):
    """
    Serializer for the incoming URL check request.
    """

    url = serializers.URLField(max_length=2048, help_text="The URL to check.")


class URLCheckResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for the response of a URL check.
    """

    class Meta:
        model = URLCheck
        fields = [
            "id",
            "url_to_check",
            "is_phishing",
            "in_phishtank_database",
            "phishtank_id",
            "details_url",
            "checked_at",
        ]
