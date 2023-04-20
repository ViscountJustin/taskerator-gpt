from Environment import SLACK_APP_TOKEN, SLACK_BOT_TOKEN
from SlackWrapper import SlackWrapper
import re

slackwrapper = SlackWrapper(SLACK_BOT_TOKEN, SLACK_APP_TOKEN)

def log(message: str):
    cleanMessage = re.sub('\[[0-9a-zA-Z]*\[[0-9a-zA-Z]*', '', message)
    print(message)
    with open('somefile.txt', 'a') as the_file:
        the_file.write(cleanMessage+'\n')
    slackwrapper.send_slack_message('taskerator-gpt', cleanMessage)