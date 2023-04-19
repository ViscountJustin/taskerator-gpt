import os
from SlackWrapper import SlackWrapper
import re

SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")

slackwrapper = SlackWrapper(SLACK_BOT_TOKEN, SLACK_APP_TOKEN)

def log(message: str):
    cleanMessage = re.sub('\[[0-9a-zA-Z]*\[[0-9a-zA-Z]*', '', message)
    print(message)
    with open('somefile.txt', 'a') as the_file:
        the_file.write(cleanMessage+'\n')
    if(SLACK_BOT_TOKEN):
        slackwrapper.send_slack_message('taskerator-gpt', cleanMessage)