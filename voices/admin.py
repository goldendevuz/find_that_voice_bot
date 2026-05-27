from django.contrib import admin
from .models import BotUser, Voice

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'joined_at')
    search_fields = ('telegram_id', 'username', 'first_name')

@admin.register(Voice)
class VoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'description', 'usage_count', 'created_at')
    search_fields = ('description', 'owner__username', 'owner__telegram_id')
    list_filter = ('created_at',)
    readonly_fields = ('file_id', 'file_unique_id')
