from .models import LiveChatSettings

def livechat_settings(request):
    try:
        settings = LiveChatSettings.objects.first()
    except LiveChatSettings.DoesNotExist:
        settings = None
    return {'livechat_settings': settings}