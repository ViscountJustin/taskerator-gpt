from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

class SlackWrapper:
    def __init__(self, bot_token, app_token):
        self.bot_token = bot_token
        self.app_token = app_token

    def send_slack_message(self, channel: str, message: str):
        try:
            slack_client = WebClient(token=self.bot_token)
            slack_client.chat_postMessage(channel=channel, text=message)
        except Exception as e:
            print(f"Error sending message to Slack: {e}")