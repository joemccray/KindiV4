from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"ok": True})


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # This endpoint will be protected
def whoami(request):
    """
    A simple test endpoint to verify authentication and return user claims.
    """
    return Response(
        {
            "sub": getattr(request.clerk, "sub", None),
            "claims": request.clerk,
        }
    )
