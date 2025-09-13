from django.contrib import admin

from .models import Indicator, ThreatReport


class ThreatReportInline(admin.TabularInline):
    model = ThreatReport
    extra = 0
    readonly_fields = ("report_type", "fetched_at", "raw_data")
    can_delete = False


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ("value", "type", "last_seen")
    list_filter = ("type",)
    search_fields = ("value",)
    readonly_fields = ("id", "first_seen", "last_seen")
    inlines = [ThreatReportInline]


@admin.register(ThreatReport)
class ThreatReportAdmin(admin.ModelAdmin):
    list_display = ("indicator", "report_type", "fetched_at")
    list_filter = ("report_type",)
    search_fields = ("indicator__value",)
    readonly_fields = ("id", "fetched_at", "indicator", "raw_data")
