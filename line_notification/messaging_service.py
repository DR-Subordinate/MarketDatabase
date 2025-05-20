from linebot import LineBotApi
from linebot.models import TextSendMessage
from .models import LineUser
from django.conf import settings

class LineMessagingService:
    def __init__(self):
        self.api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

    def send_message(self, line_user_id, message):
        self.api.push_message(line_user_id, TextSendMessage(text=message))

    def send_to_all(self, message):
        """Send to all registered LINE users"""
        for user in LineUser.objects.all():
            self.send_message(user.line_user_id, message)
