from django.db import models
from django.utils import timezone
import uuid


class TimestampBase(models.Model):
    """
    Abstract base model with timestamps and common utilities.
    """

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
        ordering = ["-created"]
        get_latest_by = "created"

    @property
    def age_seconds(self):
        """
        Returns object age in seconds.
        """
        return (timezone.now() - self.created).total_seconds()


class UUIDBase(models.Model):
    """
    Abstract base model with UUID primary key.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True


class BotUser(TimestampBase):
    """
    Telegram user model.
    Telegram ID is used as the primary key because it is already globally unique.
    """

    telegram_id = models.BigIntegerField(primary_key=True)

    language = models.CharField(
        max_length=5,
        default="uz",
    )

    username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=255,
    )

    joined_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta(TimestampBase.Meta):
        db_table = "voices_botuser"

    def __str__(self):
        return self.username or self.first_name or str(self.telegram_id)


class Voice(UUIDBase, TimestampBase):
    """
    Stored Telegram voice/audio reference.
    """

    owner = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        related_name="voices",
    )

    file_id = models.CharField(
        max_length=255,
    )

    file_unique_id = models.CharField(
        max_length=255,
    )

    description = models.TextField(
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    usage_count = models.PositiveIntegerField(
        default=0,
    )

    class Meta(TimestampBase.Meta):
        db_table = "voices_voice"

        constraints = [
            models.UniqueConstraint(
                fields=["owner", "file_unique_id"],
                name="unique_voice_per_user",
            )
        ]

        indexes = [
            models.Index(fields=["file_unique_id"]),
            models.Index(fields=["usage_count"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.owner} - {self.description[:30]}"
