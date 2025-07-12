import os
import numpy as np
from analytical.params.testcase import params
from analytical.model.zardi2015_model import WaveResolutions
from analytical.data_definition.analytical_netcdf_writer import AnalyticalNetcdfWriter
from common.netcdf_writer import DatasetToNetcdf
from common.filename_generator import make_dir_and_filename, nowstr
from visualization.common.io_utils import load_all_data, stack_by_variable, convert_to_standard_shapes
from visualization.plot_time_alt_map import plot_ubar_thetabar

def main():
    params_model = {k: v for k, v in params.items() if k != "output"}
    # 1. モデル計算
    model = WaveResolutions(**params_model)
    results = model.solve()   # 全時刻・高度分の2次元配列、1次元時系列配列

    times = results["time"]
    print("times: ", times)
    nt = len(times)
    output_root = params["output_root"] if "output_root" in params else params["output"]
    planet = params["planet"]
    flow_regime = results["regime"] if "regime" in results else None
    date_str = nowstr()

    # 2. 1時間(or dtごと)のデータをNetCDF保存
    for i, t_now in enumerate(times):
        # 1時刻分を抽出
        
        single_result = {k: (v[i] if isinstance(v, (list, np.ndarray)) and len(v) == nt else v)
                         for k, v in results.items()}

        single_result["u_bar"] = single_result["u_bar"][:, i:i+1]
        single_result["theta_bar"] = single_result["theta_bar"][:, i:i+1]
        #print(str(i)+": ", single_result["u_bar"].shape)
        single_result["time"] = np.array([t_now])
        
        #print(single_result)
        #input("stop")
        # ディレクトリ・ファイル名生成
        dir_path, fname = make_dir_and_filename(
            params, mode="analytical", flow_regime=flow_regime, current_time=t_now, date_str=date_str
        )
        os.makedirs(dir_path, exist_ok=True)
        save_path = os.path.join(dir_path, fname)
        #print(save_path)
        # 保存
        writer = AnalyticalNetcdfWriter(single_result, params)
        writer.save(save_path)

    # 3. 保存先ディレクトリから全ファイル読み込み
    varnames = ["u_bar", "theta_bar", "altitude", "time", "K"]
    data_list = load_all_data(dir_path, varnames)
    stacked = stack_by_variable(data_list, varnames)
    reshaped_stacked = convert_to_standard_shapes(stacked)

    # 4. 可視化
    methods = ["scatter", "pcolormesh"]

    for method in methods:
        save_filename = f"time_alt_map_{method}.png"
        title=f"Analytical solution ({planet}, regime: {flow_regime})"
        plot_ubar_thetabar(
            t_array=reshaped_stacked["time"],
            altitude=reshaped_stacked["altitude"],
            u_bar=reshaped_stacked["u_bar"],
            theta_bar=reshaped_stacked["theta_bar"],
            K = reshaped_stacked["K"],
            period=params.get("period", 24*3600),
            save_path=os.path.join(dir_path, save_filename),
            title=title,
            method=method
        )

if __name__ == "__main__":
    main()
