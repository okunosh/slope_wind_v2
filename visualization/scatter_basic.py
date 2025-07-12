import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

def plot_scatter_ubar_thetabar(
    t_array,             # 時間[sec] (1次元 or 2次元可)
    altitude_array,      # 高度[m] (1次元)
    u_bar,               # [時間, 高度] (2次元)
    theta_bar,           # [時間, 高度] (2次元)
    period=24*3600,      # 1日の秒数（火星 or 地球）
    cmap="bwr",
    save_path=None,
    title=None,
    show_colorbar=True
):
    """
    t_array: (時間数,) もしくは (時間数, 高度数)配列でもOK
    altitude_array: (高度数,)
    u_bar, theta_bar: (時間数, 高度数)
    period: 地方時変換用
    """
    # meshgridに変換
    if t_array.ndim == 1:
        T, Z = np.meshgrid(t_array, altitude_array, indexing='ij')
    else:
        T, Z = t_array, altitude_array[None, :]

    local_time = (t_array / period * 24) % 24

    local_time_2d = np.repeat(t_array[:, None], altitude_array.shape[1], axis=1)  # shape: (9, 16)#16????
    local_time = (local_time_2d.flatten() / period * 25) % 25#24???????

    print("period: ", period)
    print("t_array.shape: ", t_array.shape, t_array)
    print("local_time.shape: ", local_time.shape)
    print("altitude_array.shape: ", altitude_array.shape)
    print("u_bar.shape: ", u_bar.shape)
    print("theta_bar.shape: ", theta_bar.shape)
    print("T.shape: ", T.shape)
    print("Z.shape: ", Z.shape)


    vmin = min(np.nanmin(u_bar), np.nanmin(theta_bar))
    vmax = max(np.nanmax(u_bar), np.nanmax(theta_bar))
    norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    cmap = "bwr"

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True, sharex=True)
    fontsize_label = 14
    fontsize_title = 18
    fontsize_tick = 12

    # (1) u_bar
    sc0 = axes[0].scatter(local_time.flatten(), altitude_array.flatten(), c=u_bar.flatten(), cmap=cmap, s=20, marker="s")
    axes[0].set_ylabel('Altitude [m]', fontsize=fontsize_label)
    axes[0].set_title(r'(a) wind speed $\overline{u}$ [m/s]', fontsize=fontsize_title)
    #if show_colorbar:
        #plt.colorbar(sc0, ax=axes[0], orientation='vertical', fraction=0.045, pad=0.04)

    # (2) theta_bar
    sc1 = axes[1].scatter(local_time.flatten(), altitude_array.flatten(), c=theta_bar.flatten(), cmap=cmap, s=20, marker="s")
    axes[1].set_xlabel('Local Time [hour]', fontsize=fontsize_label)
    axes[1].set_ylabel('Altitude [m]', fontsize=fontsize_label)
    axes[1].set_title(r"(b) potential temperature anomaly $\overline{\theta}$ [K]", fontsize=fontsize_title)
    if show_colorbar:
        plt.colorbar(sc1, ax=axes, orientation='vertical', fraction=0.045, pad=0.04)

    for ax in axes:
        ax.tick_params(axis='x', labelsize=fontsize_tick)
        ax.tick_params(axis='y', labelsize=fontsize_tick)
        ax.grid()

    if title:
        fig.suptitle(title, fontsize=fontsize_title)

    #plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Fig is saved: {save_path}")
        plt.close()
    else:
        plt.show()
        plt.close()

if __name__ == "__main__":
    import argparse
    import os
    from visualization.common.io_utils import load_all_data, stack_by_variable
    
    parser = argparse.ArgumentParser(description='Plot u_bar and theta_bar from NetCDF files in a directory.')
    parser.add_argument('directory', type=str, help='Directory containing NetCDF files')
    args = parser.parse_args()

    varnames = ["u_bar", "theta_bar", "altitude", "time"]
    data_list = load_all_data(args.directory, varnames)
    stacked = stack_by_variable(data_list, varnames)
    t_array = stacked["time"]#.flatten()
    altitude = stacked["altitude"]#.flatten()

    # 4. 可視化
    plot_scatter_ubar_thetabar(
        t_array=t_array,
        altitude_array=altitude,
        u_bar=stacked["u_bar"],
        theta_bar=stacked["theta_bar"],
        period=24*3600,
        save_path=None,
        title=None
        )
