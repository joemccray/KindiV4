from rest_framework import serializers


class SerpApiQuerySerializer(serializers.Serializer):
    """
    Serializer for the incoming search query.
    """

    query = serializers.CharField(max_length=2048, help_text="The search query.")
    # Add other common parameters like 'location' if needed in the future
    # location = serializers.CharField(max_length=255, required=False)
