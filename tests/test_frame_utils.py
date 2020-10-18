from tgintegration.utils.frame_utils import get_caller_function_name


def test_get_caller_function_name():
    def foo():
        return bar()

    def bar():
        return get_caller_function_name()

    assert foo() == "foo"


def test_get_caller_function_name_lambda():
    def foo():
        f = lambda: get_caller_function_name()  # noqa
        return f()

    assert foo() == "foo"
