import argparse
import os
import sys
from datetime import datetime

from visualization.common.io_utils import (
    load_all_data, stack_by_variable, convert_to_standard_shapes
)
from results_validation.get_extremas import extract_extremas
from results_validation.plot_extremas import plot_extrema_scatter_comparison
from results_validation.plot_differences import plot_differences  # 差分描画
import numpy as np

import shutil

def check_shapes_and_abort(old_vars, new_vars, save_dir):
    """
    u_bar と theta_bar の shape を比較し、どれか一致しなければディレクトリ削除して終了。

    Parameters
    ----------
    old_vars : dict
        旧モデルの変数辞書
    new_vars : dict
        新モデルの変数辞書
    save_dir : str
        保存先ディレクトリ（不一致時に削除）
    """
    varnames = ["u_bar", "theta_bar"]
    mismatches = []

    for var in varnames:
        shape_old = old_vars[var].shape
        shape_new = new_vars[var].shape
        if shape_old != shape_new:
            mismatches.append(f"{var}: old: {shape_old}, new: {shape_new}")

    if mismatches:
        print("[ERROR] The following variable shapes do not match:")
        for msg in mismatches:
            print("  ", msg)

        print("[INFO] The shape of 'u_bar' or 'theta_bar' does not match between old and new results.")
        print("[INFO] If you still want to compare the results, use '--mode extrema' instead.")
        print(f"[INFO] Removing result directory: {save_dir}")
        shutil.rmtree(save_dir, ignore_errors=True)
        raise ValueError("Shape mismatch detected. Aborting.")

def main():
    # -------------------
    # コマンドライン引数
    # -------------------
    parser = argparse.ArgumentParser(description="Compare results and visualize extrema or difference.")
    parser.add_argument("--old", required=True, help="Path to old results directory")
    parser.add_argument("--new", required=True, help="Path to new results directory")
    parser.add_argument("--comparison_type", required=True, choices=[
        "analytical_old_vs_new",
        "numerical_old_vs_new",
        "analytical_vs_numerical"
    ], help="Type of comparison")
    parser.add_argument("--mode", required=True, choices=["extrema", "difference"],
                        help="Comparison mode: 'extrema' or 'difference'")

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
    for k in varnames:
        print(f"  {k:<10}: {old_vars[k].shape}")
    print("New:")
    for k in varnames:
        print(f"  {k:<10}: {new_vars[k].shape}")

    # -------------------
    # 保存ディレクトリの準備
    # -------------------
    now = datetime.now().strftime("%Y%m%dT%H%M%S")
    save_root = os.path.join("results_validation", args.comparison_type)
    save_dir = os.path.join(save_root, f"{now}_results_comparison_{args.mode}")
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
    # 処理の分岐
    # -------------------
    if args.mode == "extrema":
        # 極値比較
        extrema_old_u = extract_extremas(old_vars, varname="u_bar")
        extrema_old_theta = extract_extremas(old_vars, varname="theta_bar")
        extrema_new_u = extract_extremas(new_vars, varname="u_bar")
        extrema_new_theta = extract_extremas(new_vars, varname="theta_bar")

        plot_extrema_scatter_comparison(
            extrema_old_u, extrema_new_u,
            extrema_old_theta, extrema_new_theta,
            z_altitude=new_vars["altitude"],
            cmap="coolwarm",
            save_path=os.path.join(save_dir, "extrema_scatter.png")
        )
        print(f"[INFO] Extrema figure saved to: {save_dir}")

    elif args.mode == "difference":
        # 差分比較（配列の大きさが一致する前提）
        check_shapes_and_abort(old_vars, new_vars, save_dir)
        diff_u = new_vars["u_bar"] - old_vars["u_bar"]
        diff_theta = new_vars["theta_bar"] - old_vars["theta_bar"]

        plot_differences(
            diff_u, diff_theta,
            time=new_vars["time"],
            z_altitude=new_vars["altitude"],
            cmap="coolwarm",
            save_path=os.path.join(save_dir, "difference_plot.png")
        )
        print(f"[INFO] Difference figure saved to: {save_dir}")

if __name__ == "__main__":
    main()
