import os
import json
import time
from langchain_community.callbacks import get_openai_callback
from .langchain_init import openai_costs, reset_openai_costs
from functools import wraps
from rich import print

logs = []

def withcosts(reason):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Running {func.__name__} with costs")
            input_data = str((args, kwargs))
            input_size = len(input_data)
            start_time = time.time()
            
            reset_openai_costs()
            result = func(*args, **kwargs)
            
            output_data = str(result)
            output_size = len(output_data)

            end_time = time.time()

            total_size = input_size + output_size
            elapsed_time = end_time - start_time

            log = {
                "reason": reason,
                "function": func.__name__,
                "openai": openai_costs,
                "io": {
                    "input_size": input_size,
                    "output_size": output_size,
                    "total_size": total_size,
                    "input": input_data,
                    "output": output_data,
                },
                "time": elapsed_time,
            }
            logs = []
            if os.path.exists("logs.json"):
                logs = json.load(open("logs.json"))
            logs.append(log)
            json.dump(logs, open("logs.json", "w"), indent=4)

            print(log)
        return wrapper

    return decorator


def logging(func):
    def wrapper(*args, **kwargs):
        input_data = str((args, kwargs))
        input_size = len(input_data)

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        output_data = str(result)
        output_size = len(output_data)

        total_bandwidth = input_size + output_size
        elapsed_time = end_time - start_time

        logs.append(
            {
                "function": func.__name__,
                "input_size": input_size,
                "output_size": output_size,
                "total_size": total_bandwidth,
                "elapsed_time": elapsed_time,
            }
        )
        return result

    return wrapper
