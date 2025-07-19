import argparse
import os
import sys
from datetime import datetime

from visualization.common.io_utils import (
    load_all_data, stack_by_variable, convert_to_standard_shapes
)
from results_validation.get_extremas import extract_extremas
from results_validation.plot_results_comparison import plot_extrema_scatter_comparison

def main():
    # -------------------
    # コマンドライン引数
    # -------------------
    parser = argparse.ArgumentParser(description="Compare results and visualize extrema.")
    parser.add_argument("--old", required=True, help="Path to old results directory")
    parser.add_argument("--new", required=True, help="Path to new results directory")
    parser.add_argument("--comparison_type", required=True, choices=[
        "analytical_old_vs_new",
        "numerical_old_vs_new",
        "analytical_vs_numerical"
    ], help="Type of comparison")

    args = parser.parse_args()

    # -------------------
    # データ読み込み
    # -------------------
    varnames = ["u_bar", "theta_bar", "altitude", "time"]
    print("[INFO] Loading old data...")
    old_data = load_all_data(args.old, varnames)
    old_stacked = stack_by_variable(old_data, varnames)
    old_vars = convert_to_standard_shapes(old_stacked)

    print("[INFO] Loading new data...")
    new_data = load_all_data(args.new, varnames)
    new_stacked = stack_by_variable(new_data, varnames)
    new_vars = convert_to_standard_shapes(new_stacked)

    print("[INFO] Data loaded successfully. Shapes:")
    print("Old:")
    for k in ["u_bar", "theta_bar", "altitude", "time"]:
        print(f"  {k:<10}: {old_vars[k].shape}")
    print("New:")
    for k in ["u_bar", "theta_bar", "altitude", "time"]:
        print(f"  {k:<10}: {new_vars[k].shape}")

    # -------------------
    # 極値の抽出
    # -------------------
    extrema_old_u = extract_extremas(old_vars, varname="u_bar")
    extrema_old_theta = extract_extremas(old_vars, varname="theta_bar")
    extrema_new_u = extract_extremas(new_vars, varname="u_bar")
    extrema_new_theta = extract_extremas(new_vars, varname="theta_bar")

    # -------------------
    # 保存ディレクトリの準備
    # -------------------
    now = datetime.now().strftime("%Y%m%dT%H%M%S")
    save_root = os.path.join("results_validation", args.comparison_type)
    save_dir = os.path.join(save_root, f"{now}_results_comparison")
    os.makedirs(save_dir, exist_ok=True)

    # -------------------
    # コマンド引数の記録
    # -------------------
    args_txt_path = os.path.join(save_dir, "commandline_args.txt")
    with open(args_txt_path, "w") as f:
        f.write("Executed command:\n")
        f.write(" ".join(sys.argv) + "\n\n")
        
        f.write("Parsed arguments:\n")
        for key, value in vars(args).items():
            f.write(f"{key}: {value}\n")


    # -------------------
    # 描画
    # -------------------
    plot_extrema_scatter_comparison(
        extrema_old_u, extrema_new_u,
        extrema_old_theta, extrema_new_theta,
        z_altitude=new_vars["altitude"],
        cmap="bwr",
        save_path=os.path.join(save_dir, "extrema_scatter.png")
    )

    print(f"[INFO] Figure saved to: {save_dir}")

if __name__ == "__main__":
    main()
