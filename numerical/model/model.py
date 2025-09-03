import numpy as np

class NumericalModel:
    def __init__(self, altitude, times, alpha_rad, dt):
        self.altitude = np.asarray(altitude, dtype=float)   # (nz,)
        self.times = np.asarray(times, dtype=float)         # (nt,)
        self.nz = len(self.altitude)
        self.nt = len(self.times)
        self.alpha = float(alpha_rad)
        self.dt = float(dt)

        if self.nz < 2:
            raise ValueError("nz must be >= 2")
        # Δn は与えられた高度座標から平均で推定（等間隔前提）
        self.dn = float(np.mean(np.diff(self.altitude)))
        print("dn: ", self.dn)

        # 現行APIに合わせて“列ベクトル(2D)”で保持
        self.u_bar = np.zeros((self.nz, 1))           # 最終時刻のみ（必要なら後で (nz,nt) に拡張）
        self.theta_bar = np.zeros((self.nz, 1))
        self.w = np.zeros((2 * self.nz, 1))           # [u(0..nz-1); theta(0..nz-1)] の縦ベクトル

    # --- 三重対角ブロックを構築 ---
    def update_block_matrix(self, K_col, B_col, C_col):
        """
        K_col, B_col, C_col: 各時刻の鉛直プロファイル（shape (nz,) 推奨）
        戻り値: 2*nz × 2*nz のブロック行列 [[A, B],[C, D]]
        """
        K = np.asarray(K_col, dtype=float).reshape(-1)
        Bdiag = np.asarray(B_col, dtype=float).reshape(-1)
        Cdiag = np.asarray(C_col, dtype=float).reshape(-1)

        inv_dn2 = 1.0 / (self.dn * self.dn)
        r = K * (self.dt * inv_dn2)                    # r_i = K_i * dt / dn^2

        # --- A, D: 三重対角（内部点）---
        A = np.zeros((self.nz, self.nz), dtype=float)
        D = np.zeros((self.nz, self.nz), dtype=float)
        for i in range(1, self.nz - 1):
            ri = float(r[i])
            #A[i, i-1] = ri
            A[i+1,i] = ri 
            A[i, i  ] = 1.0 - 2.0 * ri
            A[i, i+1] = ri

            #D[i, i-1] = ri
            D[i+1, i] = ri
            D[i, i  ] = 1.0 - 2.0 * ri
            D[i, i+1] = ri

        D[1,0] = r[1]
        # 端の行は“値保持”にしておき、更新後に境界条件を適用（安定）
        A[0, :] = 0.0; #A[0, 0] = 1.0
        A[-1,:] = 0.0; #A[-1,-1] = 1.0
        A[:,-1] = 0.0
        #D[0, :] = 0.0; D[0, 0] = 1.0
        D[-1,:] = 0.0; #D[-1,-1] = 1.0
        D[:,-1] = 0.0
        # --- B, C: 対角結合 ---
        B = np.diag(Bdiag)                             # θ → u（浮力）
        C = np.diag(Cdiag)                             # u → θ（背景温位傾度）

        B[0,0] = 0
        B[self.nz-1, self.nz-1] = 0
        C[0,0] = 0
        C[self.nz-1, self.nz-1] = 0

        """
        print("A (0..2,0..2)=\n", A[:3,:3])   # A[1,0] が ri になっているか
        print("A (-3:-1, -3:-1)=\n", A[-3:,-3:])
        print("D (0..2,0..2)=\n", D[:3,:3])   # D[1,0] が ri になっているか
        print("D (-3:-1, -3:-1)=\n", D[-3:, -3:])
        input("stop")
        """
        
        # ブロック結合
        block_matrix = np.block([[A, B],
                                 [C, D]])
        #print("block_matrix: ", block_matrix)
        return block_matrix

    def step(self, t_idx, K_col, gamma_col, surface_temp, g, theta_0):
        """
        t_idx: 時刻インデックス
        K_col, gamma_col: shape (nz,)
        surface_temp: この時刻の地表温位（スカラー）
        g, theta_0: スカラー
        """
        gamma = np.asarray(gamma_col, dtype=float).reshape(-1)
        gamma_clip = np.clip(gamma, 1e-6, None)        # 0割回避は少し強めに
        N = np.sqrt((g / float(theta_0)) * gamma_clip) # [1/s]

        # 結合係数（ベクトル）
        B = self.dt * (N**2) * np.sin(self.alpha) / gamma_clip   # θ→u
        C = -self.dt * gamma_clip * np.sin(self.alpha)           # u→θ

        # 行列で更新
        matrix = self.update_block_matrix(K_col, B, C)           # (2nz,2nz)
        self.w = matrix @ self.w                                 # (2nz,1)

        # --- 境界条件の適用（更新後に直接）---
        # 分割ビュー（列ベクトル形状を維持）
        u = self.w[:self.nz, 0]
        th = self.w[self.nz:, 0]

        # u: 上下 Neumann 0（端は隣をコピー）
        u[0]      = u[1]
        u[-1]     = u[-2]
        # theta: 下端 Dirichlet（地表強制）, 上端 Neumann 0
        th[0]     = float(surface_temp)
        th[-1]    = th[-2]

        # 結合して戻す
        self.w[:self.nz, 0]  = u
        self.w[self.nz:, 0]  = th

        # 数値健全性チェック
        if not np.isfinite(self.w).all():
            raise FloatingPointError(f"Non-finite encountered at t_idx={t_idx}")

        # 出力（現行の (nz,1) に合わせて“最後時刻のみ”を反映）
        self.u_bar[:, 0]     = u
        self.theta_bar[:, 0] = th

        #print("u_bar:", self.u_bar)
        #print("theta_bar: ", self.theta_bar)
        #input("continue")
