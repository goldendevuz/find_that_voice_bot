from django.contrib import admin
from .models import BotUser, Voice


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 10

    class Meta:
        abstract = True

@admin.register(BotUser)
class BotUserAdmin(BaseAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'joined_at')
    search_fields = ('telegram_id', 'username', 'first_name')

@admin.register(Voice)
class VoiceAdmin(BaseAdmin):
    list_display = ('id', 'owner', 'description', 'usage_count', 'created_at')
    search_fields = ('description', 'owner__username', 'owner__telegram_id')
    list_filter = ('created_at',)
    readonly_fields = ('file_id', 'file_unique_id')
