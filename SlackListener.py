from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import Environment

class SlackListener:
    def __init__(self, user_input_handler):
        self.bot_token = Environment.SLACK_BOT_TOKEN
        self.app_token = Environment.SLACK_APP_TOKEN
        self.app = App(token=Environment.SLACK_BOT_TOKEN)
        self.user_input_handler = user_input_handler
        @self.app.command("/dotask")
        def handle_command(ack, respond, command):
            # Acknowledge command request
            ack()
            user_input = command['text']
            print('user input:')
            print(user_input)
            # Process the user input and generate a response
            response = self.user_input_handler(user_input)  # Implement this function according to your requirements
            # Send the response back to the user
            respond(response)
        handler = SocketModeHandler(self.app, self.app_token)
        handler.start()
