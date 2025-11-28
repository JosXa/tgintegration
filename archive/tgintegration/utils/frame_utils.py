import inspect


def get_caller_function_name() -> str:
    return inspect.stack()[2].function
