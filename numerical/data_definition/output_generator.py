import numpy as np

def generate_output_dict(model, t_idx, fields, surface_temp):
    """
    model: シミュレーションモデル（u_bar, theta_bar, altitude, times を持つ）
    t_idx: 現在の時間ステップインデックス
    fields: 事前計算済みの物理量の辞書（gamma, K, N, N_alpha, omega±, l±, theta, rho, p）
    surface_temp: 地表温度配列 (time,)
    """
    return {
        "u_bar": model.u_bar,  # shape: (altitude, 1)
        "theta_bar": model.theta_bar,  # shape: (altitude, 1)
        "altitude": model.altitude,  # shape: (altitude,)
        "time": np.array([model.times[t_idx]]),

        "gamma": fields["gamma"][:, t_idx:t_idx+1],
        "K": fields["K"][:, t_idx:t_idx+1],
        "N": fields["N"][:, t_idx:t_idx+1],
        "N_alpha": fields["N_alpha"][:, t_idx:t_idx+1],
        "omega_plus": fields["omega_plus"][:, t_idx:t_idx+1],
        "omega_minus": fields["omega_minus"][:, t_idx:t_idx+1],
        "l_plus": fields["l_plus"][:, t_idx:t_idx+1],
        "l_minus": fields["l_minus"][:, t_idx:t_idx+1],
        "theta": fields["theta"][:, t_idx:t_idx+1],
        #"rho": fields["rho"][:, t_idx:t_idx+1],
        #"p": fields["p"],

        "surface_temp": surface_temp[t_idx:t_idx+1],  # shape: (1,)
    }
