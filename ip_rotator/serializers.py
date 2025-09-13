from rest_framework import serializers

from .models import ApiGatewayProxy


class ApiGatewayProxySerializer(serializers.ModelSerializer):
    """
    Serializer for the ApiGatewayProxy model.
    """

    class Meta:
        model = ApiGatewayProxy
        fields = [
            "id",
            "target_site",
            "aws_region",
            "api_id",
            "endpoint_url",
            "status",
            "last_used",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
