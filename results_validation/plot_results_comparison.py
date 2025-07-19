import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm
import matplotlib.lines as mlines

def plot_extrema_scatter_comparison(
    extrema_old_u, extrema_new_u,
    extrema_old_theta, extrema_new_theta,
    z_altitude,
    cmap="bwr",
    save_path=None
):
    """
    共通カラーマップとマーカー形状で old/new を比較表示する描画関数

    Parameters
    ----------
    extrema_old_u, extrema_new_u : dict
    extrema_old_theta, extrema_new_theta : dict
    z_altitude : ndarray
        new データの高度軸
    cmap : str
        共通のカラーマップ（例: "coolwarm"）
    save_path : str or None
        保存ファイルパス（Noneなら plt.show()）
    """

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), sharex=True)

    # 共通設定
    marker_size = 64
    edge_color = 'black'

    zmin = np.min(z_altitude)
    zmax = np.max(z_altitude)

    # 共通 TwoSlopeNorm（old + new の値すべて）
    all_vals = np.concatenate([
        extrema_old_u["max_val"], extrema_old_u["min_val"],
        extrema_old_theta["max_val"], extrema_old_theta["min_val"],
        extrema_new_u["max_val"], extrema_new_u["min_val"],
        extrema_new_theta["max_val"], extrema_new_theta["min_val"]
    ])
    norm = TwoSlopeNorm(vmin=np.min(all_vals), vcenter=0.0, vmax=np.max(all_vals))

    times = extrema_old_u["time"] / 3600
    xticks = np.arange(np.floor(times[0] / 6) * 6, np.ceil(times[-1] / 6) * 6 + 1, 6)

    for ax in axes:
        ax.set_facecolor("lightgray")

    # --- 上段：u_bar ---
    ax1 = axes[0]
    ax1.scatter(times, extrema_old_u["z_max"], c=extrema_old_u["max_val"],
                cmap=cmap, norm=norm, marker='o', alpha=0.6,
                s=marker_size, edgecolors=edge_color)
    ax1.scatter(times, extrema_old_u["z_min"], c=extrema_old_u["min_val"],
                cmap=cmap, norm=norm, marker='o', alpha=0.6,
                s=marker_size, edgecolors=edge_color)
    ax1.scatter(times, extrema_new_u["z_max"], c=extrema_new_u["max_val"],
                cmap=cmap, norm=norm, marker='x',
                s=marker_size, edgecolors=edge_color)
    ax1.scatter(times, extrema_new_u["z_min"], c=extrema_new_u["min_val"],
                cmap=cmap, norm=norm, marker='x',
                s=marker_size, edgecolors=edge_color)
    ax1.set_ylabel("altitude [m]")
    ax1.set_title("Extrema of u_bar")
    ax1.set_ylim(zmin, zmax)
    ax1.set_xticks(xticks)
    ax1.grid(True)

    # --- 下段：theta_bar ---
    ax2 = axes[1]
    ax2.scatter(times, extrema_old_theta["z_max"], c=extrema_old_theta["max_val"],
                cmap=cmap, norm=norm, marker='o', alpha=0.6,
                s=marker_size, edgecolors=edge_color)
    ax2.scatter(times, extrema_old_theta["z_min"], c=extrema_old_theta["min_val"],
                cmap=cmap, norm=norm, marker='o', alpha=0.6,
                s=marker_size, edgecolors=edge_color)
    ax2.scatter(times, extrema_new_theta["z_max"], c=extrema_new_theta["max_val"],
                cmap=cmap, norm=norm, marker='x',
                s=marker_size, edgecolors=edge_color)
    ax2.scatter(times, extrema_new_theta["z_min"], c=extrema_new_theta["min_val"],
                cmap=cmap, norm=norm, marker='x',
                s=marker_size, edgecolors=edge_color)
    ax2.set_ylabel("altitude [m]")
    ax2.set_xlabel("Local Time [h]")
    ax2.set_title("Extrema of theta_bar")
    ax2.set_ylim(zmin, zmax)
    ax2.set_xticks(xticks)
    ax2.grid(True)

    # 凡例（マーカー形状で old/new を区別）
    legend_old = mlines.Line2D([], [], color='black', marker='o', linestyle='None',
                               markersize=8, label='Old model')
    legend_new = mlines.Line2D([], [], color='black', marker='x', linestyle='None',
                               markersize=8, label='New model')
    ax1.legend(handles=[legend_old, legend_new], loc='upper right')
    ax2.legend(handles=[legend_old, legend_new], loc='upper right')

    # --- カラーバー（共通） ---
    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    cb = plt.colorbar(ax1.collections[2], cax=cbar_ax)  # new の 1 つから取得

    plt.subplots_adjust(left=0.1, right=0.9, hspace=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300)
        print(f"[INFO] Saved figure to: {save_path}")
    else:
        plt.show()
