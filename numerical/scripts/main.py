import numpy as np
import xarray as xr
import os
import sys
from datetime import datetime

#from common.multiple_params_loade import load_netcdf_vars, load_all_data
from visualization.common.io_utils import load_all_data
from common.filename_generator import make_dir_and_filename, nowstr
from common.multiple_params_loader import load_params_module, load_multiple_params
from numerical.model.model import NumericalModel
from numerical.data_definition.field_computation import compute_physical_fields
from numerical.data_definition.output_generator import generate_output_dict
from numerical.data_definition.numerical_netcdf_writer import NumericalDatasetToNetcdf
from visualization.common.io_utils import stack_by_variable, convert_to_standard_shapes
from visualization.plot_time_alt_map import plot_ubar_thetabar


def main(params):
    # 座標生成
    z = np.arange(0, params["z_max"] + params["dz"], params["dz"])
    print("len(z)=",len(z))
    times = np.arange(0, params["t_max"] + params["dt"], params["dt"])
    #print(times.shape)

     # 検証用の定数配列を直接生成（NetCDFファイルを使わない）
    expected_nz = 261
    expected_nt = int(times.shape[0])#int(params["t_max"] / params["dt"]) + 1
    omega = 2 * np.pi / params["period"]

    gamma = np.full((expected_nz, expected_nt), 0.003)
    K = np.full((expected_nz, expected_nt), 3.0)
    surface_temp = 5.0 * np.sin(omega * np.arange(expected_nt) * params["dt"])

    nz, nt = gamma.shape

    """
    # NetCDFからの実データ読み込み
    gamma = load_netcdf_vars(params["gamma_file"], "gamma")
    K = load_netcdf_vars(params["K_file"], "K")
    surface_temp = load_netcdf_vars(params["surface_temp_file"], "theta_0")
    nz, nt = gamma.shape
    """
    # 入力配列の形状検証
    #expected_nz = int(params["z_max"] / params["dz"]) + 1
    #expected_nt = int(params["t_max"] / params["dt"]) + 1
    if gamma.shape != (expected_nz, expected_nt):
        raise ValueError(f"gamma の形状が不正です: 期待値=({expected_nz},{expected_nt}) 実際={gamma.shape}")
    if K.shape not in [(expected_nz, expected_nt), (expected_nt,)]:
        raise ValueError(f"K の形状が不正です: 期待値=({expected_nz},{expected_nt}) または ({expected_nt},) 実際={K.shape}")
    if surface_temp.shape[0] != expected_nt:
        raise ValueError(f"surface_temp の時間次元が不正です: 期待値={expected_nt} 実際={surface_temp.shape[0]}")

    theta_bar = np.ones((nz, nt)) * np.nan
    print("theta_bar.shape: ", theta_bar.shape)

    # 事前計算
    fields = compute_physical_fields(
        gamma=gamma,
        K=K,
        g=params["g"],
        theta_0=params["theta_0"],
        alpha_deg=params["alpha_deg"],
        omega=2 * np.pi / params["period"],
        params=params,
        results={"theta_bar": theta_bar},
        planet=params["planet"]
    )

    print("[INFO] fields calculated")
    # モデル初期化
    model = NumericalModel(z, times, np.radians(params["alpha_deg"]), params["dt"])

    # ディレクトリ・ファイル名生成の準備
    date_str = nowstr()
    dir_path = None  # 最初の保存時にセットする

    # 時間ループ（1時間ごと保存）
    for t_idx, t in enumerate(times):
        K_col = K[:, t_idx]
        gamma_col = gamma[:, t_idx]
        T_sfc = surface_temp[t_idx]

        model.step(t_idx, K_col, gamma_col, T_sfc, params["g"], params["theta_0"])

        if t % params["output_interval"] == 0:
            # 出力ディレクトリを最初の保存時に作成
            if dir_path is None:
                dir_path, _ = make_dir_and_filename(
                    params,
                    mode="numerical",
                    flow_regime=None,
                    current_time=t,
                    date_str=date_str
                )
                os.makedirs(dir_path, exist_ok=True)

            # ファイル名生成
            _, fname = make_dir_and_filename(
                params,
                mode="numerical",
                flow_regime=None,
                current_time=t,
                date_str=date_str
            )
            save_path = os.path.join(dir_path, fname)

            # theta・rho を更新
            fields["theta"][:, t_idx:t_idx+1] = (
                params["theta_0"] + gamma[:, t_idx:t_idx+1] * z[:, np.newaxis] + model.theta_bar
            )
            #R = 192 if params["planet"] == "Mars" else 287
            #cp = 730 if params["planet"] == "Mars" else 1004
            #exponent = R / cp
            #p0 = 610 if params["planet"] == "Mars" else 101325
            #p_z = fields["p"][:, np.newaxis]
            #T = fields["theta"][:, t_idx:t_idx+1] * (p_z / p0)**exponent

            #fields["rho"][:, t_idx:t_idx+1] = p_z / (R * T)

            results = generate_output_dict(model, t_idx, fields, surface_temp)
            writer = NumericalDatasetToNetcdf(results, params)
            writer.save(save_path)

    # 3. 保存先ディレクトリから全ファイル読み込み
    print("making figures...")

    varnames = ["u_bar", "theta_bar", "altitude", "time", "K"]
    data_list = load_all_data(dir_path, varnames)
    stacked = stack_by_variable(data_list, varnames)
    reshaped_stacked = convert_to_standard_shapes(stacked)

    
    # 4. 可視化
    methods = ["scatter", "pcolormesh"]
    for method in methods:
        save_filename = f"time_alt_map_{method}.png"  # ファイル保存せず画面表示の場合
        title = None
        plot_ubar_thetabar(
            t_array=reshaped_stacked["time"],
            altitude=reshaped_stacked["altitude"],
            u_bar=reshaped_stacked["u_bar"],
            theta_bar=reshaped_stacked["theta_bar"],
            K=reshaped_stacked["K"],
            period=params.get("period", 24 * 3600),
            save_path=os.path.join(dir_path, save_filename) if save_filename else None,
            title=title,
            method=method
        )


if __name__ == "__main__":
    import argparse
    if len(sys.argv) != 2:
        print("Usage: python main.py path/to/params.py")
        sys.exit(1)
    param_path = sys.argv[1]

    parser = argparse.ArgumentParser(description="execute analytical model calculation with multiple parms")
    parser.add_argument(
        "parameter_files",
        nargs="+",
        help="params files in analytical/params/, DO NOT include directory! ONLY filename",
    )
    args = parser.parse_args()
    
    for config_path, params in load_multiple_params(args.parameter_files, "numerical/params"):
        print(f"[INFO] start {config_path}")
        main(params)
        #run_single_case(config_path, params)
    #params = load_params_module(param_path, "numerical/params")
    #main(params)
