from django.db import models
import uuid
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with UUID PK, timestamps, and common utilities.
    All models should inherit from this class.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Timestamp when the object was created",
    )
    modified = models.DateTimeField(
        auto_now=True,
        verbose_name="Modified At",
        help_text="Timestamp when the object was last modified",
    )

    class Meta:
        abstract = True
        ordering = ["-created"]  # Default ordering: newest first
        get_latest_by = "created"

    def __str__(self):
        """
        Returns a string representation.
        If the model has a 'name' or 'title' attribute, return it, else UUID.
        """
        for attr in ["name", "title", "full_name"]:
            if hasattr(self, attr):
                value = getattr(self, attr)
                if value:
                    return str(value)
        return str(self.id)

    def save(self, *args, **kwargs):
        """
        Can be overridden in child models for custom pre-save behavior.
        """
        super().save(*args, **kwargs)

    @property
    def age_seconds(self):
        """
        Returns the age of the object in seconds since creation.
        """
        return (timezone.now() - self.created).total_seconds()


class BotUser(BaseModel):
    telegram_id = models.BigIntegerField(unique=True)
    language = models.CharField(max_length=5, default='uz')
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.first_name or str(self.telegram_id)
    

class Voice(BaseModel):
    owner = models.ForeignKey(BotUser, on_delete=models.CASCADE, related_name='voices')
    file_id = models.CharField(max_length=255)
    file_unique_id = models.CharField(max_length=255)
    description = models.TextField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    usage_count = models.PositiveIntegerField(default=0)

    class Meta:
        # Prevent the same user from saving the exact same voice twice
        # or maybe we just allow it? The prompt says "NEVER reupload files, reuse Telegram cached file_id". 
        # But maybe a user wants to tag the same voice multiple times? Let's just keep it simple.
        constraints = [
            models.UniqueConstraint(fields=['owner', 'file_unique_id'], name='unique_voice_per_user')
        ]

    def __str__(self):
        return f"{self.owner} - {self.description[:30]}"
