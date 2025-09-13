from django.contrib import admin

from .models import URLCheck


@admin.register(URLCheck)
class URLCheckAdmin(admin.ModelAdmin):
    list_display = (
        "url_to_check",
        "is_phishing",
        "in_phishtank_database",
        "checked_at",
    )
    list_filter = ("is_phishing", "in_phishtank_database")
    search_fields = ("url_to_check",)
    readonly_fields = ("id", "checked_at", "raw_response")
