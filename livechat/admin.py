from django.contrib import admin
from .models import LiveChatSettings

@admin.register(LiveChatSettings)
class LiveChatSettingsAdmin(admin.ModelAdmin):
    list_display = ('enabled', 'widget_id')