from slack_sdk import WebClient

class SlackWrapper:
    def __init__(self, bot_token, app_token):
        self.bot_token = bot_token
        self.app_token = app_token

    def send_slack_message(self, channel: str, message: str, thread_ts: str = None):
        try:
            slack_client = WebClient(token=self.bot_token)
            response = slack_client.chat_postMessage(channel=channel, text=message, thread_ts=thread_ts)
            return {"ts": response["ts"]}
        except Exception as e:
            print(f"Error sending message to Slack: {e}")
            return None
