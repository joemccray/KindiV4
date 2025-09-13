from django.contrib import admin

from .models import PersonProfile, SearchQuery


class PersonProfileInline(admin.TabularInline):
    model = PersonProfile
    extra = 0
    readonly_fields = ("full_name", "job_title", "company_name", "email")
    can_delete = False
    show_change_link = True


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "created_at", "completed_at")
    list_filter = ("status",)
    readonly_fields = (
        "id",
        "created_at",
        "completed_at",
        "reachstream_batch_id",
        "query_filter",
    )
    inlines = [PersonProfileInline]


@admin.register(PersonProfile)
class PersonProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "job_title", "company_name", "search_query")
    search_fields = ("full_name", "job_title", "company_name", "email")
    readonly_fields = ("id", "created_at", "search_query", "raw_data")
