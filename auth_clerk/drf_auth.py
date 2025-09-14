from __future__ import annotations

import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.utils.functional import cached_property
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from .claims import ClaimsPolicyError, validate_claims
from .jwks import JWKSClient


class ClerkAuthentication(BaseAuthentication):
    www_authenticate_realm = "clerk"

    @cached_property
    def jwks_client(self) -> JWKSClient:
        return JWKSClient(settings.CLERK_JWKS_URL)

    def authenticate(self, request) -> tuple[User, dict] | None:
        token = self._get_token_from_request(request)
        if not token:
            return None  # No credentials presented

        try:
            header = jwt.get_unverified_header(token)
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed("Invalid token header") from e

        kid = header.get("kid")
        key = None
        if kid:
            if jwk := self.jwks_client.get_key(kid):
                key = jwt.PyJWK(jwk).key  # builds cryptography key
            else:
                raise exceptions.AuthenticationFailed("Unknown key id (rotation?)")
        # Verify signature and basic time claims with small skew
        try:
            payload = jwt.decode(
                token,
                key=key,
                algorithms=["RS256", "EdDSA"],  # Clerk supports RSA & EdDSA
                options={"require": ["exp", "iat"]},
                leeway=settings.CLERK_MAX_CLOCK_SKEW_SEC,
                audience=settings.CLERK_ALLOWED_AUDIENCES or None,
                issuer=settings.CLERK_ISSUER,
            )
        except jwt.ExpiredSignatureError as e:
            # Signal to the client it should refresh the token and retry
            raise exceptions.AuthenticationFailed("Token expired") from e
        except jwt.InvalidIssuerError as e:
            raise exceptions.AuthenticationFailed("Invalid issuer") from e
        except jwt.InvalidAudienceError as e:
            raise exceptions.AuthenticationFailed("Invalid audience") from e
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(str(e)) from e

        # Extra policy checks (azp, optional aud list)
        try:
            validate_claims(payload)
        except ClaimsPolicyError as e:
            raise exceptions.AuthenticationFailed(str(e)) from e

        # Map Clerk user to Django user (stateless). For API-only apps return AnonymousUser w/ payload.
        django_user = AnonymousUser()
        django_user.clerk_sub = payload.get("sub")  # user id
        django_user.clerk_sid = payload.get("sid")  # session id
        request.clerk = payload  # attach claims for views

        return (django_user, payload)

    def authenticate_header(self, request) -> str:
        # Enables DRF to send WWW-Authenticate on 401
        return f'Bearer realm="{self.www_authenticate_realm}"'

    def _get_token_from_request(self, request) -> str | None:
        # Authorization: Bearer <token>
        auth = get_authorization_header(request).decode("utf-8")
        if auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1].strip()
        # Optional cookie-based (same-origin)
        if settings.CLERK_ACCEPT_COOKIE:
            if cookie := request.COOKIES.get("__session"):
                return cookie
        return None
