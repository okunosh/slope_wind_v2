import os
import re
import numpy as np
import xarray as xr

def extract_time_from_filename(filename):
    """ファイル名からt******部分を抽出（例: _t0345600.nc → 345600）"""
    m = re.search(r'_t(\d{6})\.nc$', filename)
    return int(m.group(1)) if m else None

def list_netcdf_files_sorted(directory):
    """ディレクトリ内のNetCDFファイルをt******順にソートして返す"""
    files = [f for f in os.listdir(directory) if f.endswith('.nc')]
    files_with_time = []
    for f in files:
        t_val = extract_time_from_filename(f)
        if t_val is not None:
            files_with_time.append((t_val, f))
    files_sorted = [f for t, f in sorted(files_with_time)]
    return files_sorted

def load_all_data(directory, varnames):
    """
    指定ディレクトリ内のnetcdfファイルを時系列順に全て読み、
    指定した変数(varnames)を欠損時はnp.nanで埋めて辞書のリストで返す。
    """
    files_sorted = list_netcdf_files_sorted(directory)
    data_list = []
    for fname in files_sorted:
        ds = xr.open_dataset(os.path.join(directory, fname))
        data = {}
        for v in varnames:
            if v in ds:
                data[v] = ds[v].values
            else:
                # 欠損時は最小限のnp.nan（shape決めが難しい場合は0次元で）
                data[v] = np.nan
        data_list.append(data)
        ds.close()
    return data_list

def stack_by_variable(data_list, varnames):
    """
    data_list（ファイルごと辞書のリスト）を
    変数ごとの2次元配列（[ファイル数, ...shape]）に変換して返すdict。
    欠損（np.nan）が混じる場合は型やshapeに注意（object型で返る場合も）。
    """
    result = {}
    for v in varnames:
        # ファイルごとに該当変数をリストアップ
        vals = [d[v] if not isinstance(d[v], float) or not np.isnan(d[v]) else None for d in data_list]
        # shape推定（すべて欠損の場合はスキップ）
        if all(x is None for x in vals):
            result[v] = np.array([np.nan]*len(vals))
        else:
            # 欠損値が混じる場合は、最初に見つかった非欠損shapeに揃えてnp.nanで埋める
            valid = [x for x in vals if x is not None]
            target_shape = valid[0].shape if valid else ()
            arr = []
            for x in vals:
                if x is None:
                    arr.append(np.full(target_shape, np.nan))
                else:
                    arr.append(x)
            result[v] = np.stack(arr)
    return result

# ---- 使用例 ----
# output_dir = "output/Analytical/results_ver01/Mars/..."
# varnames = ["u_bar", "theta_bar", "K"]
# data_list = load_all_data(output_dir, varnames)
# stacked = stack_by_variable(data_list, varnames)
# print(stacked["u_bar"].shape)  # → (ファイル数, ...空間方向)
