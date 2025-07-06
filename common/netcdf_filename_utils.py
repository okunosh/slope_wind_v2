from datetime import datetime

def float2str(v):
    if v is None:
        return "var"
    return str(v).replace(".", "p")

def nowstr():
    return datetime.now().strftime("%Y%m%dT%H%M%S")

def results_or_tests_dir(is_testcase: bool) -> str:
    return "tests" if is_testcase else "results"

def zero_pad_time(t):
    return f"{int(t):06d}"
