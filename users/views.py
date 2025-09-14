from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class ClerkWebhookSyncView(APIView):
    """
    A view to handle incoming webhooks from Clerk for user synchronization.

    This endpoint is unsecured (`AllowAny`) because it relies on webhook
    signature verification for security, which will be added later.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handles user.created, user.updated, and user.deleted events from Clerk.

        For now, it just acknowledges the webhook receipt.
        """
        # In a real implementation, we would:
        # 1. Verify the webhook signature.
        # 2. Parse the request body to get the event type and data.
        # 3. Create, update, or delete a KindiUser based on the event.
        # 4. Log the payload for debugging.

        # For this scaffolding step, we simply return a success response.
        return Response(data={"message": "Webhook received"}, status=status.HTTP_200_OK)
