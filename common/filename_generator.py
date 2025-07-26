from datetime import datetime
import os

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

def make_dir_and_filename(params, mode, flow_regime, current_time, date_str):
    """
    is_testcaseによってtests/resultsに分岐
    output/Analytical/ver01/tests(Earth...)/... または results/...
    """
    #date_str = nowstr()
    planet = params.get("planet", "Unknown")
    user_subdir = params.get("output", "run")  # "ver01"など
    is_testcase = params.get("is_testcase", False)
    result_dir = results_or_tests_dir(is_testcase)

    alpha = float2str(params.get("alpha_deg", params.get("alpha", 0)))
    dt = float2str(params.get("dt", 0))
    dz = float2str(params.get("dz", 0))

    if mode == "analytical":
        gamma = float2str(params.get("gamma", 0))
        regime = flow_regime if flow_regime else "UnknownRegime"
        dir_name = f"{date_str}_{regime}_alp{alpha}_gamma{gamma}_dt{dt}_dn{dz}"
        fname = f"A_{date_str}_{regime}_t{zero_pad_time(current_time)}.nc"
        root_dir = os.path.join("output", "Analytical", user_subdir, result_dir, planet, dir_name)
    elif mode == "numerical":
        dir_name = f"{date_str}_alp{alpha}_dt{dt}_dn{dz}"
        fname = f"N_{date_str}_t{zero_pad_time(current_time)}.nc"
        root_dir = os.path.join("output", "Numerical", user_subdir, result_dir, planet, dir_name)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return root_dir, fname
