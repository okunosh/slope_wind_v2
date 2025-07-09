import matplotlib.pyplot as plt
import numpy as np

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

    local_time = (T / period * 24) % 24

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    fontsize_label = 14
    fontsize_title = 18
    fontsize_tick = 12

    # (1) u_bar
    sc0 = axes[0].scatter(local_time.flatten(), Z.flatten(), c=u_bar.flatten(), cmap=cmap, s=20, marker="s")
    axes[0].set_ylabel('Altitude [m]', fontsize=fontsize_label)
    axes[0].set_title(r'(a) wind speed $\overline{u}$ [m/s]', fontsize=fontsize_title)
    if show_colorbar:
        plt.colorbar(sc0, ax=axes[0], orientation='vertical', fraction=0.045, pad=0.04)

    # (2) theta_bar
    sc1 = axes[1].scatter(local_time.flatten(), Z.flatten(), c=theta_bar.flatten(), cmap=cmap, s=20, marker="s")
    axes[1].set_xlabel('Local Time [hour]', fontsize=fontsize_label)
    axes[1].set_ylabel('Altitude [m]', fontsize=fontsize_label)
    axes[1].set_title(r"(b) potential temperature anomaly $\overline{\theta}$ [K]", fontsize=fontsize_title)
    if show_colorbar:
        plt.colorbar(sc1, ax=axes[1], orientation='vertical', fraction=0.045, pad=0.04)

    for ax in axes:
        ax.tick_params(axis='x', labelsize=fontsize_tick)
        ax.tick_params(axis='y', labelsize=fontsize_tick)
        ax.grid()

    if title:
        fig.suptitle(title, fontsize=fontsize_title)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"Fig is saved: {save_path}")
        plt.close()
    else:
        plt.show()
        plt.close()

if __name__ == "__main__":

    
    plot_scatter_ubar_thetabar(
    t_array=sub_time,            # 選択範囲の時間[sec]配列
    altitude_array=sub_altitude, # 選択範囲の高度配列
    u_bar=sub_ubar,              # (時間数, 高度数)
    theta_bar=sub_theta,         # (時間数, 高度数)
    period=24*3600,
    save_path="output/scatter_test.png",
    title="Test Case: Mars, 4th Day"
    )
