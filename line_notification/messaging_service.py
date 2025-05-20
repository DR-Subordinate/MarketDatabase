from linebot import LineBotApi
from linebot.models import TextSendMessage
from django.conf import settings

class LineMessagingService:
    def __init__(self):
        self.api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

    def send_message(self, line_user_id, message):
        self.api.push_message(line_user_id, TextSendMessage(text=message))
