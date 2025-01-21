#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Use first 11 rows, other cl_wide_mem_rw variants are handled in a different script
df_u50_slow = pd.read_csv("../data/u50-slow-vitis.csv", skipinitialspace=True)
df_u50_fast = pd.read_csv("../data/u50-fast-vitis.csv", skipinitialspace=True)
df_u280_slow = pd.read_csv("../data/u280-slow-vitis.csv", skipinitialspace=True)
df_u280_fast = pd.read_csv("../data/u280-fast-vitis.csv", skipinitialspace=True)
df_u280_ddr_slow = pd.read_csv("../data/u280-ddr-slow-vitis.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv("../data/u280-ddr-fast-vitis.csv", skipinitialspace=True)

dfs = [df_u50_slow, df_u280_slow, df_u280_ddr_slow, df_u50_fast, df_u280_fast, df_u280_ddr_fast]

# Get ratio of individual times to combined time
for df in dfs:
    df["transfer+kernel"] = df["data_to_fpga_ocl"] + df["kernel_ocl"] + df["data_to_host_ocl"]
    df["data_to_fpga_ocl"] /= df["transfer+kernel"]
    df["kernel_ocl"] /= df["transfer+kernel"]
    df["data_to_host_ocl"] /= df["transfer+kernel"]

bar_width = 0.1
colors = {
    "to_fpga": "tab:blue",
    "kernel": "tab:orange",
    "to_host": "tab:green"
}
app_names = df_u50_slow["app_name"].values
x = np.arange(len(app_names))
x_offset = -3 * bar_width

for df in dfs:
    bottom = np.zeros(len(app_names))

    vals = df["data_to_fpga_ocl"].values
    plt.bar(x + x_offset, vals, bar_width, bottom, color=colors["to_fpga"])
    bottom += vals

    vals = df["kernel_ocl"].values
    plt.bar(x + x_offset, vals, bar_width, bottom, color=colors["kernel"])
    bottom += vals

    vals = df["data_to_host_ocl"].values
    plt.bar(x + x_offset, vals, bar_width, bottom, color=colors["to_host"])

    x_offset += bar_width * 1.3

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Time")

patches = [
    mpatches.Patch(color=colors["to_fpga"], label="Data transfer to FPGA"),
    mpatches.Patch(color=colors["kernel"], label="Kernel execution"),
    mpatches.Patch(color=colors["to_host"], label="Data transfer to Host")
]
plt.legend(handles=patches)

plt.tight_layout()

filename = "../plots/time-breakdown.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")


