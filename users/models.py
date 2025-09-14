from django.db import models


class KindiUser(models.Model):
    """
    Represents a user in the system, with data synced from Clerk.
    """

    # Clerk's user ID is a string, not a standard UUID.
    clerk_id = models.CharField(
        max_length=255, primary_key=True, unique=True, editable=False
    )
    email = models.EmailField(unique=True, help_text="User's email address.")
    first_name = models.CharField(
        max_length=150, blank=True, help_text="User's first name."
    )
    last_name = models.CharField(
        max_length=150, blank=True, help_text="User's last name."
    )
    image_url = models.URLField(
        max_length=2048, blank=True, help_text="URL for the user's profile image."
    )

    # Using JSONField to store flexible metadata like roles and permissions.
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Application-specific user metadata (e.g., role, permissions).",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Kindi User"
        verbose_name_plural = "Kindi Users"
        ordering = ["-created_at"]
