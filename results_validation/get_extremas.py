import numpy as np

def extract_extremas(data, varname="u_bar"):
    """
    指定変数について、時間ごとの最大値・最小値とその高度を返す

    Parameters
    ----------
    data : dict
        標準化されたデータ辞書（"u_bar", "theta_bar", "altitude", "time" を含む）
    varname : str
        処理対象の変数名（例: "u_bar" または "theta_bar"）

    Returns
    -------
    result : dict
        {
            "time": ...,  # shape (nt,)
            "z_max": ...,  # 最大値を取る高度, shape (nt,)
            "max_val": ...,  # 最大値, shape (nt,)
            "z_min": ...,  # 最小値を取る高度, shape (nt,)
            "min_val": ...,  # 最小値, shape (nt,)
        }
    """
    var = data[varname]  # shape: (nt, nz)
    z = data["altitude"]
    t = data["time"]

    nt, nz = var.shape
    if z.shape[0] != nz:
        raise ValueError("高度方向の次元が一致しません")

    # 転置して (nz, nt) にして扱う（高さごとに時系列）
    var_T = var.T  # shape: (nz, nt)

    max_idx = np.argmax(var_T, axis=0)  # shape: (nt,)
    min_idx = np.argmin(var_T, axis=0)

    result = {
        "time": t,
        "z_max": z[max_idx],
        "max_val": var_T[max_idx, np.arange(nt)],
        "z_min": z[min_idx],
        "min_val": var_T[min_idx, np.arange(nt)],
    }

    return result
