import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

def plot_differences(diff_u, diff_theta, time, z_altitude, cmap="coolwarm", save_path=None):
    """
    u_bar, theta_bar の差分を2段のpcolormeshで描画

    Parameters
    ----------
    diff_u : ndarray
        u_bar の差分 [nt, nz]
    diff_theta : ndarray
        theta_bar の差分 [nt, nz]
    time : ndarray
        時間配列（秒） [nt]
    z_altitude : ndarray
        高度配列 [nz]
    cmap : str
        使用するカラーマップ名（中央0で対称に表示するため TwoSlopeNorm 使用）
    save_path : str or None
        保存先パス（None の場合は plt.show()）
    """
    time_hours = time / 3600  # 地方時 [h]
    zmin = np.min(z_altitude)
    zmax = np.max(z_altitude)

    # カラーマップの中心を0にするための正規化
    all_vals = np.concatenate([diff_u.flatten(), diff_theta.flatten()])
    vmax = np.nanmax(np.abs(all_vals))
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), sharex=True)

    # 上段：u_bar 差分
    im1 = axes[0].pcolormesh(time_hours, z_altitude, diff_u.T,
                             shading="auto", cmap=cmap, norm=norm)
    axes[0].set_title("Difference in u_bar")
    axes[0].set_ylabel("Altitude [m]")
    axes[0].set_ylim(zmin, zmax)
    axes[0].grid(True)

    # 下段：theta_bar 差分
    im2 = axes[1].pcolormesh(time_hours, z_altitude, diff_theta.T,
                             shading="auto", cmap=cmap, norm=norm)
    axes[1].set_title("Difference in theta_bar")
    axes[1].set_ylabel("Altitude [m]")
    axes[1].set_xlabel("Local Time [h]")
    axes[1].set_ylim(zmin, zmax)
    axes[1].grid(True)

    # 横軸の目盛り（6時間ごと）
    xticks = np.arange(np.floor(time_hours[0] / 6) * 6, np.ceil(time_hours[-1] / 6) * 6 + 1, 6)
    axes[1].set_xticks(xticks)

    # カラーバー（共通）
    cbar = fig.colorbar(im2, ax=axes, orientation="vertical", fraction=0.025, pad=0.02)
    cbar.ax.yaxis.set_offset_position('right')
    cbar.ax.yaxis.get_offset_text().set_x(1.5)



    plt.subplots_adjust(left=0.1, right=0.85, hspace=0.15)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight", pad_inches=0.05)
        print(f"[INFO] Saved difference plot to: {save_path}")
    else:
        plt.show()
