from rest_framework import serializers

from .models import PersonProfile, SearchQuery


class PersonProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonProfile
        fields = [
            "id",
            "full_name",
            "job_title",
            "company_name",
            "email",
            "linkedin_url",
            "created_at",
        ]


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = [
            "id",
            "status",
            "error_message",
            "created_at",
            "completed_at",
        ]


class SearchQueryCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new search. Takes the filter as input.
    """

    filter = serializers.JSONField()

    def validate_filter(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Filter must be a JSON object.")
        # Add more specific validation of the filter structure if needed
        return value
