from typing import Type
from attackmate.executors.baseexecutor import BaseExecutor
import inspect


class ExecutorFactory:
    def __init__(self):
        self._executors = {}

    def register_executor(self, command_type: str):
        def decorator(cls: Type[BaseExecutor]):
            self._executors[command_type] = cls
            return cls

        return decorator

    def create_executor(self, command_type: str, **kwargs) -> BaseExecutor:
        executor_cls = self._executors.get(command_type)
        if not executor_cls:
            raise ValueError(f'Executor not found for command type: {command_type}')

        # Filter kwargs to match the executor's __init__ signature
        init_signature = inspect.signature(executor_cls.__init__)
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in init_signature.parameters}

        return executor_cls(**filtered_kwargs)


executor_factory = ExecutorFactory()
