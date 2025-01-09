#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_u50_slow = pd.read_csv("../data/u50-slow-vitis.csv", skipinitialspace=True)
df_u50_fast = pd.read_csv("../data/u50-fast-vitis.csv", skipinitialspace=True)
df_u280_slow = pd.read_csv("../data/u280-slow-vitis.csv", skipinitialspace=True)
df_u280_fast = pd.read_csv("../data/u280-fast-vitis.csv", skipinitialspace=True)
df_u280_ddr_slow = pd.read_csv("../data/u280-ddr-slow-vitis.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv("../data/u280-ddr-fast-vitis.csv", skipinitialspace=True)

dfs = [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]
fpga_configs = ["u50_hbm_200mhz", "u50_hbm_unlimited", "u280_hbm_200mhz",
                "u280_hbm_unlimited", "u280_ddr_200mhz", "u280_ddr_unlimited"]

# Sum up data transfer + kernel execution time
for df in [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]:
    df["transfer+kernel"] = df["data_to_fpga_average"] + df["kernel_average"] + df["data_to_host_average"]
    df["transfer+kernel"] /= 1_000_000 # to miliseconds

df_combined = pd.concat(dfs, ignore_index=True)
apps = df_u50_slow["app_name"].values
num_apps = len(apps)

print("app_name,slowest_time,slowest_fpga,fastest_time,fastest_fpga,speedup")

for app in apps:
    print(app, end=",")
    idxmax = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].idxmax()
    max = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].max()
    max_fpga = fpga_configs[int(idxmax / num_apps)]
    print(f"{max},{max_fpga},", end="")

    idxmin = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].idxmin()
    min = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].min()
    min_fpga = fpga_configs[int(idxmin / num_apps)]
    print(f"{min},{min_fpga},", end="")

    speedup = max / min
    print(speedup)
