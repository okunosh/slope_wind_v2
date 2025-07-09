from common.netcdf_writer import DatasetToNetcdf
import numpy as np

class AnalyticalNetcdfWriter(DatasetToNetcdf):
    def to_xarray(self):
        # from common
        ds = super().to_xarray()
        
        # unique variables to analytical solution
        nt = len(self.results["time"])
        
        # 各変数を(time,)配列として取得・保存
        def arr(key):
            v = self.results.get(key)
            if v is None:
                return None
            # 定数なら(time,)にする
            if np.isscalar(v):
                return np.full(nt, v)
            return v
        
        special_vars = {
            "gamma":      {"units": "K/m",  "description": "Potential temperature lapse rate"},
            "K":          {"units": "m^2/s", "description": "Diffusion coefficient"},
            "N":          {"units": "1/s",   "description": "BruntVäisälä frequency"},
            "N_alpha":    {"units": "1/s",   "description": "Slope-parallel BruntVäisälä frequency"},
            "omega_plus": {"units": "1/s",   "description": "N_alpha + omega"},
            "omega_minus":{"units": "1/s",   "description": "N_alpha - omega"},
            "l_plus":     {"units": "m",     "description": "Diffusive length scale (plus)"},
            "l_minus":    {"units": "m",     "description": "Diffusive length scale (minus)"},
            "psi":        {"units": "rad",   "description": "Initial phase"},
        }
        for k, meta in special_vars.items():
            v = arr(k)
            if v is not None:
                ds[k] = (("time",), v, meta)
        
        # 解析解特有の属性
        flow_regime = self.results.get("regime", None)
        if flow_regime is not None:
            ds.attrs["flow_regime"] = flow_regime

        return ds
