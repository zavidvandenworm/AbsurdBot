import asyncio
from asyncio import wait_for, TimeoutError as AsyncioTimeoutError

from concurrent.futures.process import ProcessPoolExecutor
from typing import Callable

from modules.logger import create_logger

logger = create_logger("task manager")
class TaskResult:
    def __init__(self, result: object, success: bool, message: str | None = None):
        self.result = result
        self.success = success
        self.message = message

class TaskManager:
    def __init__(self):
        self.JOB_LIMIT = 5
        self.JOB_TIME_LIMIT = 50
        try:
            self.task_loop = asyncio.get_running_loop()
        except RuntimeError:
            self.task_loop = asyncio.new_event_loop()
        self.executor = ProcessPoolExecutor(max_workers=self.JOB_LIMIT)

    async def run(self, func: Callable, *args) -> TaskResult:
        func_future = self.task_loop.run_in_executor(self.executor, func, *args)

        try:
            callable_result = await wait_for(func_future, timeout=self.JOB_TIME_LIMIT)
            result = TaskResult(callable_result, True)
        except AsyncioTimeoutError:
            func_future.cancel()
            result = TaskResult(None, False, f"Task timed out after {self.JOB_TIME_LIMIT} seconds.")
        except Exception as e:
            result = TaskResult(None, False, str(e))

        return result

    def shutdown(self):
        self.executor.shutdown(wait=False)
