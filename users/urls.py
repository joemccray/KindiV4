from django.urls import path

from .views import ClerkWebhookSyncView

app_name = "users"

urlpatterns = [
    path("webhooks/sync/", ClerkWebhookSyncView.as_view(), name="clerk-webhook-sync"),
]
