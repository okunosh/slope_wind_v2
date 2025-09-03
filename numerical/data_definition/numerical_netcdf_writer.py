import xarray as xr
import numpy as np
from datetime import datetime
from common.netcdf_writer import DatasetToNetcdf

class NumericalDatasetToNetcdf(DatasetToNetcdf):
    def __init__(self, results: dict, params: dict):
        super().__init__(results, params)

        # 数値解特有の変数（いずれも (altitude, time) または (time,)）
        self.gamma = results.get("gamma")
        self.K = results.get("K")
        self.N = results.get("N")
        self.N_alpha = results.get("N_alpha")
        self.omega_plus = results.get("omega_plus")
        self.omega_minus = results.get("omega_minus")
        self.l_plus = results.get("l_plus")
        self.l_minus = results.get("l_minus")
        self.surface_temp = results.get("surface_temp")  # (time,)

        self.theta = results.get("theta")  # ← 追加：温位構造 (altitude, time)
        #self.rho = results.get("rho")      # ← 追加：密度 (altitude, time)
        #self.p = results.get("p")          # ← 追加：圧力 (altitude,)

    def to_xarray(self):
        ds = super().to_xarray()

        def add(var_name, dims, units, desc):
            value = getattr(self, var_name)
            if value is not None:
                ds[var_name] = (dims, value, {"units": units, "description": desc})

        # 2次元変数
        add("gamma", ("altitude", "time"), "K/m", "Potential temperature gradient")
        add("K", ("altitude", "time"), "m^2/s", "Eddy diffusivity")
        add("N", ("altitude", "time"), "1/s", "BruntVäisälä frequency")
        add("N_alpha", ("altitude", "time"), "1/s", "Slope-normal frequency: N·sin(alpha)")
        add("omega_plus", ("altitude", "time"), "1/s", "N_alpha + omega")
        add("omega_minus", ("altitude", "time"), "1/s", "N_alpha - omega")
        add("l_plus", ("altitude", "time"), "m", "Mixing length scale (+)")
        add("l_minus", ("altitude", "time"), "m", "Mixing length scale (-)")
        add("theta", ("altitude", "time"), "K", "Potential temperature")
        #add("rho", ("altitude", "time"), "kg/m^3", "Atmospheric density")
        #add("p", ("altitude",), "Pa", "Pressure profile (assumed exponential)")

        # 1次元変数
        add("surface_temp", ("time",), "K", "Surface potential temperature")

        return ds

    def save(self, path: str):
        ds = self.to_xarray()
        ds.to_netcdf(path)
        # print(f"[INFO] NetCDF saved to: {path}")
