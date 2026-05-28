from django.db import models
from django.utils import timezone
import uuid


class TimestampBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created"]
        get_latest_by = "created"

    @property
    def age_seconds(self):
        return (timezone.now() - self.created).total_seconds()


class UUIDBase(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True


class BotUser(TimestampBase):
    telegram_id = models.BigIntegerField(primary_key=True)

    language = models.CharField(max_length=5, default="uz")
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "voices_botuser"

    def __str__(self):
        return self.username or self.first_name or str(self.telegram_id)


class Voice(UUIDBase, TimestampBase):
    owner = models.ForeignKey(
        BotUser,
        on_delete=models.CASCADE,
        related_name="voices",
    )

    file_id = models.CharField(max_length=255)
    file_unique_id = models.CharField(max_length=255)

    description = models.TextField(db_index=True)

    usage_count = models.PositiveIntegerField(default=0)

    # CORE FEATURE FLAGS
    is_public = models.BooleanField(default=False)     # default PRIVATE
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
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
            models.Index(fields=["created"]),
            models.Index(fields=["is_public"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.owner} - {self.description[:30]}"
