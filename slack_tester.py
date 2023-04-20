from dotenv import load_dotenv
load_dotenv()
from SlackWrapper import SlackWrapper
import Environment

def user_input_handler(user_input):
    # Implement your processing logic here
    return f"You entered: {user_input}"

if __name__ == "__main__":
    slack_wrapper = SlackWrapper(Environment.SLACK_BOT_TOKEN, Environment.SLACK_APP_TOKEN, user_input_handler)
