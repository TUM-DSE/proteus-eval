#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Use first 10 rows, other cl_wide_mem_rw variants are handled in a different script
df_u50_slow = pd.read_csv("../data/u50-slow-vitis.csv", skipinitialspace=True).iloc[:10]
df_u50_fast = pd.read_csv("../data/u50-fast-vitis.csv", skipinitialspace=True).iloc[:10]
df_u280_slow = pd.read_csv("../data/u280-slow-vitis.csv", skipinitialspace=True).iloc[:10]
df_u280_fast = pd.read_csv("../data/u280-fast-vitis.csv", skipinitialspace=True).iloc[:10]
df_u280_ddr_slow = pd.read_csv("../data/u280-ddr-slow-vitis.csv", skipinitialspace=True).iloc[:10]
df_u280_ddr_fast = pd.read_csv("../data/u280-ddr-fast-vitis.csv", skipinitialspace=True).iloc[:10]

# Sum up data transfer + kernel execution time
for df in [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]:
    df["transfer+kernel"] = df["data_to_fpga_ocl"] + df["kernel_ocl"] + df["data_to_host_ocl"]

bar_width = 0.12
app_names = df_u50_slow["app_name"].values
x = np.arange(len(app_names))

# Total execution time --------------------------------------------------------------------------------------

plt.bar(x - 2 * bar_width, df_u50_slow["average"].values, width=bar_width, label=f"U50 HBM 200 MHz")
plt.bar(x - 1 * bar_width, df_u280_slow["average"].values, width=bar_width, label=f"U280 HBM 200 MHz")
plt.bar(x                , df_u280_ddr_slow["average"].values, width=bar_width, label=f"U280 DDR 200 MHz")
plt.bar(x + 1 * bar_width, df_u50_fast["average"].values, width=bar_width, label="U50 HBM unlimited")
plt.bar(x + 2 * bar_width, df_u280_fast["average"].values, width=bar_width, label="U280 HBM unlimited")
plt.bar(x + 3 * bar_width, df_u280_ddr_fast["average"].values, width=bar_width, label="U280 DDR unlimited")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average total execution time (s)")
plt.legend()
plt.tight_layout()

filename = "../plots/time-compute-total.png"
print(f"Saving figure to {filename}")
plt.savefig(filename)
plt.clf()

# Data transfer + kernel time -------------------------------------------------------------------------------

plt.bar(x - 2 * bar_width, df_u50_slow["transfer+kernel"].values, width=bar_width, label=f"U50 HBM 200 MHz")
plt.bar(x - 1 * bar_width, df_u280_slow["transfer+kernel"].values, width=bar_width, label=f"U280 HBM 200 MHz")
plt.bar(x                , df_u280_ddr_slow["transfer+kernel"].values, width=bar_width, label=f"U280 DDR 200 MHz")
plt.bar(x + 1 * bar_width, df_u50_fast["transfer+kernel"].values, width=bar_width, label="U50 HBM unlimited")
plt.bar(x + 2 * bar_width, df_u280_fast["transfer+kernel"].values, width=bar_width, label="U280 HBM unlimited")
plt.bar(x + 3 * bar_width, df_u280_ddr_fast["transfer+kernel"].values, width=bar_width, label="U280 DDR unlimited")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Data transfer + kernel time (s)")
# plt.grid(which="both", axis="y")
plt.yscale("log")
plt.legend()
plt.tight_layout()

filename = "../plots/time-compute-fpga.png"
print(f"Saving figure to {filename}")
plt.savefig(filename)
