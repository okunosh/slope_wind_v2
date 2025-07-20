import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

def plot_ubar_thetabar(
    t_array,             # (nt,) 1d
    altitude,            # (nz,) 1d
    u_bar,               # (nt, nz) 2d
    theta_bar,           # (nt, nz) 2d
    K=None,
    period=24*3600,
    cmap="bwr",
    save_path=None,
    title=None,
    show_colorbar=True,
    method="pcolormesh"  # "scatter" or "pcolormesh"
):
    """
    可視化フォーマットは変更せず、可視化手法を引数で切り替え
    """
    nt, nz = u_bar.shape

    # meshgridで2D座標配列を作成
    T, Z = np.meshgrid(t_array, altitude, indexing='ij')  # (nt, nz), (nt, nz)

    # 地方時計算
    local_time = (T / period * 24) # (nt, nz)
    """
    print(local_time)
    print("period: ", period)
    print("t_array.shape: ", t_array.shape, t_array)
    print("local_time.shape: ", local_time.shape)
    print("altitude.shape: ", altitude.shape)
    print("u_bar.shape: ", u_bar.shape)
    print("theta_bar.shape: ", theta_bar.shape)
    """
    vmin = min(np.nanmin(u_bar), np.nanmin(theta_bar))
    vmax = max(np.nanmax(u_bar), np.nanmax(theta_bar))
    norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True, sharex=True)
    fontsize_label = 14
    fontsize_title = 18
    fontsize_tick = 12

    artists = []
    for i, (arr, label, ttl) in enumerate(
        zip([u_bar, theta_bar],
            [r'(a) wind speed $\overline{u}$ [m/s]', r"(b) potential temperature anomaly $\overline{\theta}$ [K]"],
            ['Altitude [m]', 'Altitude [m]'])
    ):
        ax = axes[i]
        if method == "scatter":
            # 1次元配列に整形して描画
            c = ax.scatter(local_time.flatten(), Z.flatten(), c=arr.flatten(), cmap=cmap, norm=norm, s=20, marker="s")
        elif method == "pcolormesh":
            # 2次元配列のまま描画
            #print(local_time[:, 0])  # 1列目だけ（nt個）の値を表示
            #print(Z[0, :])           # 1行目だけ（nz個）の値を表示

            c = ax.pcolormesh(local_time, Z, arr, cmap=cmap, norm=norm, shading='auto')
        else:
            raise ValueError(f"Unknown method: {method}")
        
        artists.append(c)
        ax.set_ylabel('Altitude [m]', fontsize=fontsize_label)
        ax.set_title(label, fontsize=fontsize_title)
        ax.tick_params(axis='x', labelsize=fontsize_tick)
        ax.tick_params(axis='y', labelsize=fontsize_tick)
        ax.grid()

        if K is not None:
            ax2 = ax.twinx()
            K_bottom = K  # 最下層だけ（z=0, 1番下の高度）
            ax2.plot(local_time, K_bottom, color="k", label="K (bottom)", linewidth=1.8, alpha=0.4)
            ax2.set_ylabel("K (bottom) [m$^2$/s]", fontsize=fontsize_label, color="k")
            ax2.tick_params(axis='y', labelcolor='k', labelsize=fontsize_tick)
            ax2.spines['right'].set_color('k')
            ax2.set_yticks(np.arange(0, 101, 20))
        
    axes[1].set_xlabel('Local Time [hour]', fontsize=fontsize_label)
    axes[1].set_xticks(np.arange(0, nt, 6))
    if show_colorbar:
        #plt.colorbar(c, ax=ax, orientation='vertical', fraction=0.045, pad=0.04)
        cbar = fig.colorbar(artists[0], ax=axes, orientation='vertical', fraction=0.045, pad=0.04)
        cbar.ax.tick_params(labelsize=fontsize_tick)
    if title:
        fig.suptitle(title, fontsize=fontsize_title)

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
    from visualization.common.io_utils import load_all_data, stack_by_variable, convert_to_standard_shapes
    
    parser = argparse.ArgumentParser(description='Plot u_bar and theta_bar from NetCDF files in a directory.')
    parser.add_argument('directory', type=str, help='Directory containing NetCDF files')
    args = parser.parse_args()

    varnames = ["u_bar", "theta_bar", "altitude", "time", "K"]
    data_list = load_all_data(args.directory, varnames)
    stacked = stack_by_variable(data_list, varnames)
    reshaped_stacked = convert_to_standard_shapes(stacked)
    print(reshaped_stacked["time"].shape) #(nt,) 1d
    print(reshaped_stacked["altitude"].shape) #(nz,) 1d
    print(reshaped_stacked["u_bar"].shape) #(nt, nz) 2d
    print(reshaped_stacked["K"].shape)#(nt,) 1d anlalytical

    #input("stop")

    # 4. 可視化
    plot_ubar_thetabar(
        t_array=reshaped_stacked["time"],
        altitude=reshaped_stacked["altitude"],
        u_bar=reshaped_stacked["u_bar"],
        theta_bar=reshaped_stacked["theta_bar"],
        K = reshaped_stacked["K"],
        period=24*3600,
        save_path=None,
        title=None
        )
