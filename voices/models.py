from django.db import models

class BotUser(models.Model):
    telegram_id = models.BigIntegerField(primary_key=True)
    language = models.CharField(max_length=5, default='en')
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.first_name or str(self.telegram_id)


class Voice(models.Model):
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
