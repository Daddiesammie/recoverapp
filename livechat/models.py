from django.db import models

class LiveChatSettings(models.Model):
    enabled = models.BooleanField(default=False)
    widget_id = models.CharField(max_length=255, blank=True, null=True)
    script = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'LiveChat Settings'
        verbose_name_plural = 'LiveChat Settings'

    def __str__(self):
        return f"LiveChat Settings (Enabled: {self.enabled})"