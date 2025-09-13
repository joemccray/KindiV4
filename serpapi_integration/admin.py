from django.contrib import admin

from .models import SerpApiSearch


@admin.register(SerpApiSearch)
class SerpApiSearchAdmin(admin.ModelAdmin):
    list_display = ("engine", "created_at")
    list_filter = ("engine",)
    search_fields = ("search_parameters", "raw_response")
    readonly_fields = ("id", "created_at", "search_parameters", "raw_response")
