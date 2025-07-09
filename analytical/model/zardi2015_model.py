import numpy as np
from scipy.special import erfc

PLANET_TO_G = {"Earth": 9.81, "Mars": 3.71}

class WaveResolutions:
    def __init__(
        self,
        planet,
        alpha_deg,
        Theta,
        theta_0,
        gamma,
        omega,
        K,
        psi=0.0,
        tmax=86400,
        zmax=10000,
        dz=20.0,
        dt=3600.0,
    ):
        self.planet = planet
        self.g = PLANET_TO_G[planet]
        self.alpha_deg = alpha_deg
        self.alpha = np.deg2rad(alpha_deg)
        self.Theta = Theta
        self.theta_0 = theta_0
        self.gamma = gamma
        self.omega = omega
        self.K = K
        self.psi = psi
        self.tmax = tmax
        self.zmax = zmax
        self.dz = dz
        self.dt = dt

        # 格子生成
        self.altitude = np.arange(0, zmax + dz, dz)  # (nz+1,)
        self.time = np.arange(0, tmax + dt, dt)      # (nt+1,)
        self.nz = len(self.altitude)
        self.nt = len(self.time)

        # 計算用パラメータ
        self.N = np.sqrt(self.gamma * self.g / self.theta_0)
        self.N_alpha = self.N * np.sin(self.alpha)
        self.omega_plus = self.N_alpha + self.omega
        self.omega_minus = self.N_alpha - self.omega
        self.l_plus = np.sqrt(2 * self.K / self.omega_plus)
        self.l_minus = np.sqrt(2 * self.K / np.abs(self.omega_minus))

        self.const_u = self.Theta * self.N / (2 * self.gamma)
        self.const_theta = self.Theta / 2

    def regime(self):
        if abs(self.omega - self.N_alpha) < 1e-6:
            return "Critical"
        elif self.N_alpha < self.omega:
            return "SubCritical"
        else:
            return "SuperCritical"

    def solve(self):
        #grid points
        z = self.altitude[:, None]  # (nz+1, 1)
        t = self.time[None, :]      # (1, nt+1)
        omega_t = self.omega * t
        psi = self.psi
        regime = self.regime()

        if regime == "Critical":
            l = np.sqrt(self.K / self.N_alpha)
            eta = z / (2 * np.sqrt(self.K * t / self.omega + 1e-12))
            u_bar = self.const_u * (
                np.exp(-z / l) * np.cos(omega_t - z / l + psi)
                - erfc(eta) * np.cos(omega_t + psi)
            )
            theta_bar = self.const_theta * (
                np.exp(-z / l) * np.sin(omega_t - z / l + psi)
                + erfc(eta) * np.sin(omega_t + psi)
            )
        elif regime == "SubCritical":
            l_plus, l_minus = self.l_plus, self.l_minus
            u_bar = self.const_u * (
                np.exp(-z / l_plus) * np.cos(omega_t - z / l_plus + psi)
                - np.exp(-z / l_minus) * np.cos(omega_t - z / l_minus + psi)
            )
            theta_bar = self.const_theta * (
                np.exp(-z / l_plus) * np.sin(omega_t - z / l_plus + psi)
                + np.exp(-z / l_minus) * np.sin(omega_t - z / l_minus + psi)
            )
        else:  # SuperCritical
            l_plus, l_minus = self.l_plus, self.l_minus
            u_bar = self.const_u * (
                np.exp(-z / l_plus) * np.cos(omega_t - z / l_plus + psi)
                - np.exp(-z / l_minus) * np.cos(omega_t + z / l_minus + psi)
            )
            theta_bar = self.const_theta * (
                np.exp(-z / l_plus) * np.sin(omega_t - z / l_plus + psi)
                + np.exp(-z / l_minus) * np.sin(omega_t + z / l_minus + psi)
            )

         return {
             "planet": self.planet,
             "g": self.g,
             "alpha_deg": self.alpha_deg,
             "Theta": self.Theta,
             "theta_0": self.theta_0,
             "gamma": np.full(self.nt, self.gamma),  # (time,)で保存
             "K": np.full(self.nt, self.K),          # (time,)
             "N": np.full(self.nt, self.N),          # (time,)
             "N_alpha": np.full(self.nt, self.N_alpha),  # (time,)
             "omega_plus": np.full(self.nt, self.omega_plus),  # (time,)
             "omega_minus": np.full(self.nt, self.omega_minus), # (time,)
             "l_plus": np.full(self.nt, self.l_plus),          # (time,)
             "l_minus": np.full(self.nt, self.l_minus),        # (time,)
             "psi": np.full(self.nt, self.psi),    # (time,)
             "altitude": self.altitude,
             "time": self.time,
             "u_bar": u_bar,
             "theta_bar": theta_bar,
             "regime": regime
         }
