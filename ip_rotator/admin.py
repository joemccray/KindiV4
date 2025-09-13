from django.contrib import admin

from .models import ApiGatewayProxy


@admin.register(ApiGatewayProxy)
class ApiGatewayProxyAdmin(admin.ModelAdmin):
    list_display = ("target_site", "aws_region", "status", "last_used")
    list_filter = ("status", "aws_region")
    search_fields = ("target_site", "api_id", "endpoint_url")
    readonly_fields = ("id", "created_at", "updated_at", "last_used")
