
import time
import pinecone
from Environment import OPENAI_API_KEY, OPENAI_TEMPERATURE
from Logger import log
from SingleTaskListStorage import SingleTaskListStorage
from OpenAIWrapper import OpenAIWrapper

class TaskRunner:

    def __init__(self, join_existing, pinecone_api_key, pinecone_env, objective, tablename, initialtask, coopmode, pinecone_compat, model):
        self.join_existing = join_existing
        self.pinecone_api_key = pinecone_api_key
        self.pinecone_env = pinecone_env
        self.objective = objective
        self.tablename = tablename
        self.initialtask = initialtask
        self.coopmode = coopmode
        self.model = model
        self.openaiwrapper = OpenAIWrapper(OPENAI_TEMPERATURE, self.model, OPENAI_API_KEY, self.objective)
        self.pinecone_compat = pinecone_compat

    def RunTask(self):
        if "gpt-4" in self.model.lower():
            log(
                "\033[91m\033[1m"
                + "\n*****USING GPT-4. POTENTIALLY EXPENSIVE. MONITOR YOUR COSTS*****"
                + "\033[0m\033[0m"
            )

        log("\033[94m\033[1m" + "\n*****OBJECTIVE*****\n" + "\033[0m\033[0m")
        log(f"{self.objective}")

        if not self.join_existing: log("\033[93m\033[1m" + "\nInitial task:" + "\033[0m\033[0m" + f" {self.initialtask}")
        else: log("\033[93m\033[1m" + f"\nJoining to help the objective" + "\033[0m\033[0m")

        # Configure OpenAI and Pinecone
        pinecone.init(api_key=self.pinecone_api_key, environment=self.pinecone_env)

        # Create Pinecone index
        table_name = self.tablename
        dimension = 1536
        metric = "cosine"
        pod_type = "p1"
        if table_name not in pinecone.list_indexes():
            pinecone.create_index(
                table_name, dimension=dimension, metric=metric, pod_type=pod_type
            )

        # Connect to the index
        index = pinecone.Index(table_name)

        # Initialize tasks storage
        tasks_storage = SingleTaskListStorage()
        if self.coopmode in ['l', 'local']:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).resolve().parent))
            from extensions.ray_tasks import CooperativeTaskListStorage
            tasks_storage = CooperativeTaskListStorage(self.objective)
        elif self.coopmode in ['d', 'distributed']:
            pass


        # Get the top n completed tasks for the objective
        def context_agent(query: str, top_results_num: int):
            """
            Retrieves context for a given query from an index of tasks.

            Args:
                query (str): The query or objective for retrieving context.
                top_results_num (int): The number of top results to retrieve.

            Returns:
                list: A list of tasks as context for the given query, sorted by relevance.

            """
            query_embedding = self.openaiwrapper.get_ada_embedding(query)
            results = index.query(query_embedding, top_k=top_results_num, include_metadata=True, namespace=self.pinecone_compat)
            # log("***** RESULTS *****")
            # log(results)
            sorted_results = sorted(results.matches, key=lambda x: x.score, reverse=True)
            return [(str(item.metadata["task"])) for item in sorted_results]

        # Add the initial task if starting new objective
        if not self.join_existing:
            initial_task = {
                "task_id": tasks_storage.next_task_id(),
                "task_name": self.initialtask
            }
            tasks_storage.append(initial_task)

        # Main loop
        while True:
            # As long as there are tasks in the storage...
            if not tasks_storage.is_empty():
                # Print the task list
                log("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
                for t in tasks_storage.get_task_names():
                    log(" • "+t)

                # Step 1: Pull the first incomplete task
                task = tasks_storage.popleft()
                log("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
                log(task['task_name'])

                # Send to execution function to complete the task based on the context
                context = context_agent(query=self.objective, top_results_num=5)
                result = self.openaiwrapper.execution_agent(self.objective, task["task_name"], context)
                log("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
                log(result)

                # Step 2: Enrich result and store in Pinecone
                enriched_result = {
                    "data": result
                }  # This is where you should enrich the result if needed
                result_id = f"result_{task['task_id']}"
                vector = self.openaiwrapper.get_ada_embedding(
                    enriched_result["data"]
                )  # get vector of the actual result extracted from the dictionary
                index.upsert(
                    [(result_id, vector, {"task": task["task_name"], "result": result})],
            namespace=self.pinecone_compat
                )

                # Step 3: Create new tasks and reprioritize task list
                new_tasks = self.openaiwrapper.task_creation_agent(
                    self.objective,
                    enriched_result,
                    task["task_name"],
                    tasks_storage.get_task_names(),
                )

                for new_task in new_tasks:
                    new_task.update({"task_id": tasks_storage.next_task_id()})
                    tasks_storage.append(new_task)

                if not self.join_existing: tasks_storage.replace(self.openaiwrapper.prioritization_agent(tasks_storage.get_task_names(), tasks_storage.next_task_id()))

            time.sleep(5)  # Sleep before checking the task list again
