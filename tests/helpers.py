import functools


def cases(test_cases):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            for case in test_cases:
                new_args = args + (case if isinstance(case, tuple) else (case,))
                try:
                    func(*new_args)
                except Exception as e:
                    e.args = e.args + ('Test case: %s has been failed' % str(case), )
                    raise
        return wrapper
    return decorator