#!/usr/bin/env python3
# Load default environment variables (.env)
from dotenv import load_dotenv
load_dotenv()
from Logger import log
from TaskRunner import TaskRunner
from SlackListener import SlackListener
import Environment

def handle_user_input(self):
    runner = TaskRunner(Environment.JOIN_EXISTING_OBJECTIVE, Environment.PINECONE_API_KEY, Environment.PINECONE_ENVIRONMENT, Environment.OBJECTIVE, Environment.YOUR_TABLE_NAME, Environment.INITIAL_TASK, Environment.COOPERATIVE_MODE, Environment.OBJECTIVE_PINECONE_COMPAT, 'gpt-3.5-turbo')
    runner.RunTask()

listener = SlackListener(handle_user_input)

log("\033[95m\033[1m"+"\n*****CONFIGURATION*****\n"+"\033[0m\033[0m")
log(f"Name: {Environment.BABY_NAME}")
log(f"Mode: {'none' if Environment.COOPERATIVE_MODE in ['n', 'none'] else 'local' if Environment.COOPERATIVE_MODE in ['l', 'local'] else 'distributed' if Environment.COOPERATIVE_MODE in ['d', 'distributed'] else 'undefined'}")
log(f"Objective: {Environment.OBJECTIVE}")