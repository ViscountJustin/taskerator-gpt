import json
import time
from typing import Dict, List
import subprocess
import openai

from Logger import log


class OpenAIWrapper:

    def __init__(self, temperature, model, api_key, objective):
        self.temperature = temperature
        openai.api_key = api_key
        self.model = model
        self.api_key = api_key
        self.objective = objective

    # Get embedding for the text
    def get_ada_embedding(self, text):
        text = text.replace("\n", " ")
        return openai.Embedding.create(input=[text], model="text-embedding-ada-002")[
            "data"
        ][0]["embedding"]


    def openai_call(
        self,
        prompt: str,
        model: str = 'gpt-3.5-turbo',
        temperature: float = 0.0,
        max_tokens: int = 100,
    ):
        while True:
            try:
                if model.startswith("llama"):
                    # Spawn a subprocess to run llama.cpp
                    cmd = ["llama/main", "-p", prompt]
                    result = subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, text=True)
                    return result.stdout.strip()
                elif not model.startswith("gpt-"):
                    # Use completion API
                    response = openai.Completion.create(
                        engine=model,
                        prompt=prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=1,
                        frequency_penalty=0,
                        presence_penalty=0,
                    )
                    return response.choices[0].text.strip()
                else:
                    # Use chat completion API
                    messages = [{"role": "system", "content": prompt}]
                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        n=1,
                        stop=None,
                    )
                    return response.choices[0].message.content.strip()
            except openai.error.RateLimitError:
                log(
                    "   *** The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.error.Timeout:
                log(
                    "   *** OpenAI API timeout occured. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.error.APIError:
                log(
                    "   *** OpenAI API error occured. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.error.APIConnectionError:
                log(
                    "   *** OpenAI API connection error occured. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.error.InvalidRequestError:
                log(
                    "   *** OpenAI API invalid request. Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            except openai.error.ServiceUnavailableError:
                log(
                    "   *** OpenAI API service unavailable. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
            else:
                break

    def task_creation_agent(
        self, objective: str, result: Dict, task_description: str, task_list: List[str]
    ):
        prompt = f"""
        You are a task creation AI that uses the result of an execution agent to create new tasks with the following objective: {objective},
        The last completed task has the result: {result}.
        This result was based on this task description: {task_description}. These are incomplete tasks: {', '.join(task_list)}.
        Based on the result, create new tasks to be completed by the AI system that do not overlap with incomplete tasks.
        Return the tasks as an array."""
        response = self.openai_call(prompt)
        new_tasks = response.split("\n") if "\n" in response else [response]
        return [{"task_name": task_name} for task_name in new_tasks]


    def prioritization_agent(self, task_names, next_task_id):
        prompt = f"""
        You are a task prioritization AI tasked with cleaning the formatting of and reprioritizing the following tasks: {task_names}.
        Consider the ultimate objective of your team:{self.objective}.
        Do not remove any tasks. Return the result as a numbered list, like:
        #. First task
        #. Second task
        Start the task list with number {next_task_id}."""
        response = self.openai_call(prompt)
        new_tasks = response.split("\n") if "\n" in response else [response]
        new_tasks_list = []
        for task_string in new_tasks:
            task_parts = task_string.strip().split(".", 1)
            if len(task_parts) == 2:
                task_id = task_parts[0].strip()
                task_name = task_parts[1].strip()
                new_tasks_list.append({"task_id": task_id, "task_name": task_name})
        return new_tasks_list


    # Execute a task based on the objective and five previous tasks 
    def execution_agent(self, objective: str, task: str, context: any) -> str:
        """
        Executes a task based on the given objective and previous context.

        Args:
            objective (str): The objective or goal for the AI to perform the task.
            task (str): The task to be executed by the AI.

        Returns:
            str: The response generated by the AI for the given task.

        """
        

        # log("\n*******RELEVANT CONTEXT******\n")
        # log(context)
        prompt = f"""
        You are an AI who performs one task based on the following objective: {objective}\n.
        Take into account these previously completed tasks: {context}\n.
        Your task: {task}\nResponse:"""
        return self.openai_call(prompt, max_tokens=2000)
