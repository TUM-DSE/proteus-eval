#!/usr/bin/env python3

import pandas as pd

df_u50_slow = pd.read_csv("../data/u50-slow-vitis.csv", skipinitialspace=True)
df_u50_fast = pd.read_csv("../data/u50-fast-vitis.csv", skipinitialspace=True)
df_u280_slow = pd.read_csv("../data/u280-slow-vitis.csv", skipinitialspace=True)
df_u280_fast = pd.read_csv("../data/u280-fast-vitis.csv", skipinitialspace=True)
df_u280_ddr_slow = pd.read_csv("../data/u280-ddr-slow-vitis.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv("../data/u280-ddr-fast-vitis.csv", skipinitialspace=True)
df_freq = pd.read_csv("../data/frequencies.csv", skipinitialspace=True)

dfs_slow = [df_u50_slow, df_u280_slow, df_u280_ddr_slow]
dfs_fast = [df_u50_fast, df_u280_fast, df_u280_ddr_fast]
fpga_configs = ["u50_hbm", "u280_hbm", "u280_ddr"]

# Sum up data transfer + kernel execution time
for df in [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]:
    df["transfer+kernel"] = df["data_to_fpga_cpu"] + df["kernel_cpu"] + df["data_to_host_cpu"]

apps = df_u50_slow["app_name"].values
num_apps = len(apps)

# Best case speedup -----------------------------------------------------------------------------------------

filenames = ["speedup-best-200mhz.csv", "speedup-best-unlimited.csv"]

for i, dfs in enumerate([dfs_slow, dfs_fast]):
    print(f"Saving best case speedup data in {filenames[i]}")
    f = open(filenames[i], "w")
    f.write("app_name,slowest_time,slowest_fpga,fastest_time,fastest_fpga,speedup\n")
    df_combined = pd.concat(dfs, ignore_index=True)
    for app in apps:
        f.write(f"{app},")
        idxmax = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].idxmax()
        max = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].max()
        max_fpga = fpga_configs[int(idxmax / num_apps)]
        f.write(f"{max},{max_fpga},")

        idxmin = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].idxmin()
        min = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].min()
        min_fpga = fpga_configs[int(idxmin / num_apps)]
        f.write(f"{min},{min_fpga},")

        speedup = max / min
        f.write(f"{speedup}\n")

# Speedup of bitstream with highest clock frequency ---------------------------------------------------------

df_freq_fast = df_freq[["app_name", "u50_fast_freq", "u280_fast_freq", "u280_ddr_fast_freq"]]
filename = "speedup-freq-unlimited.csv"

print(f"Saving frequency only speedup data in {filename}")
f = open(filename, "w")
f.write("app_name,slowest_time,slowest_fpga,fastest_time,fastest_fpga,speedup\n")
df_combined = pd.concat(dfs_fast, ignore_index=True)
for app in apps:
    f.write(f"{app},")
    idxmax = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].idxmax()
    max = df_combined.loc[df_combined["app_name"] == app, "transfer+kernel"].max()
    max_fpga = fpga_configs[int(idxmax / num_apps)]
    f.write(f"{max},{max_fpga},")

    freq_max = df_freq_fast.loc[df_freq_fast["app_name"] == app, ["u50_fast_freq", "u280_fast_freq", "u280_ddr_fast_freq"]].idxmax(axis=1).iloc[0]
    if freq_max == "u50_fast_freq":
        freq_max_fpga = fpga_configs[0]
        freq_max_time = df_u50_fast.loc[df_u50_fast["app_name"] == app, "transfer+kernel"].iloc[0]
    elif freq_max == "u280_fast_freq":
        freq_max_fpga = fpga_configs[1]
        freq_max_time = df_u280_fast.loc[df_u280_fast["app_name"] == app, "transfer+kernel"].iloc[0]
    elif freq_max == "u280_ddr_fast_freq":
        freq_max_fpga = fpga_configs[2]
        freq_max_time = df_u280_ddr_fast.loc[df_u280_ddr_fast["app_name"] == app, "transfer+kernel"].iloc[0]

    f.write(f"{freq_max_time},{freq_max_fpga},")
    speedup = max / freq_max_time
    f.write(f"{speedup}\n")
