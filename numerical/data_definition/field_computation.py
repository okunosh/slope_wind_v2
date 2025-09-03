import numpy as np

PLANET_TO_P0 = {
    "Earth": 101325,  # [Pa]
    "Mars": 610       # [Pa]
}

def compute_physical_fields(gamma, K, g, theta_0, alpha_deg, omega, params, results, z=None, planet="Mars"):
    """
    事前に与えられた gamma, K から各種物理量を一括計算する。

    Parameters:
    - gamma: (z, t) ndarray, potential temperature gradient [K/m]
    - K: (z, t) ndarray, eddy diffusivity [m^2/s]
    - g: float, gravitational acceleration [m/s^2]
    - theta_0: float, reference potential temperature [K]
    - alpha_deg: float, slope angle in degrees
    - omega: float, planetary angular velocity [1/s]
    - planet: str, name of the planet ("Mars" or "Earth")

    Returns:
    dict with keys: "theta", "gamma", "K", "N", "N_alpha", "omega_plus", "omega_minus", "l_plus", "l_minus", "rho", "p"
    """

    nz, nt = gamma.shape

    if z is None:
        # 念のためのフォールバック（dzとnzから再構成／上端丸め）
        dz = params["dz"]
        z = np.linspace(0.0, (nz - 1) * dz, nz)
    z_col = z.reshape(nz, 1)  # (nz,1) に整形
    sin_alpha = np.sin(np.radians(alpha_deg))

    z_len, t_len = gamma.shape
    #dz = params["dz"]
    z_max = params["z_max"]
    # = np.arange(0, z_max + dz, dz)[:, np.newaxis]  # shape (z, 1)
    print("z", z_col)

    N = np.sqrt((g / theta_0) * gamma)  # (z, t)
    N_alpha = N * sin_alpha
    omega_plus = N_alpha + omega
    omega_minus = N_alpha - omega

    # avoid division by zero
    omega_plus = np.clip(omega_plus, 1e-8, None)
    omega_minus = np.clip(omega_minus, 1e-8, None)

    l_plus = np.sqrt(2 * K / omega_plus)
    l_minus = np.sqrt(2 * K / omega_minus)

    # θ = θ₀ + γ·z

    theta = theta_0 + gamma * z_col + results["theta_bar"]  # shape: (z, t)
    

    # 圧力分布 p(z) = p0 * exp(-z / H)
    #p0 = PLANET_TO_P0.get(planet, 610)  # fallback to Mars if unknown
    #R = 192 if planet == "Mars" else 287  # [J/kg/K], 火星 or 地球
    #cp = 730 if planet == "Mars" else 1004  # [J/kg/K]

    #H = R * theta_0 / g  # スケールハイト [m] を動的に決定
    #p = p0 * np.exp(-z / H)  # shape: (z, 1)

    # 温度 T(z, t) を計算して密度 ρ を導出
    #exponent = R / cp
    #T = theta * (p / p0)**exponent  # shape: (z, t)
    #rho = p / (R * T)  # shape: (z, t)

    return {
        "theta": theta,
        "gamma": gamma,
        "K": K,
        "N": N,
        "N_alpha": N_alpha,
        "omega_plus": omega_plus,
        "omega_minus": omega_minus,
        "l_plus": l_plus,
        "l_minus": l_minus,
        #"rho": rho,
        #"p": p.squeeze()  # shape: (z,)
    }
