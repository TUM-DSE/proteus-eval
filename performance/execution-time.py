#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import common

# Use first 11 rows, other cl_wide_mem_rw variants are handled in a different script
df_u50_slow = pd.read_csv("../data/u50-slow-vitis.csv", skipinitialspace=True).iloc[:11]
df_u50_fast = pd.read_csv("../data/u50-fast-vitis.csv", skipinitialspace=True).iloc[:11]
df_u280_slow = pd.read_csv("../data/u280-slow-vitis.csv", skipinitialspace=True).iloc[:11]
df_u280_fast = pd.read_csv("../data/u280-fast-vitis.csv", skipinitialspace=True).iloc[:11]
df_u280_ddr_slow = pd.read_csv("../data/u280-ddr-slow-vitis.csv", skipinitialspace=True).iloc[:11]
df_u280_ddr_fast = pd.read_csv("../data/u280-ddr-fast-vitis.csv", skipinitialspace=True).iloc[:11]

# Sum up data transfer + kernel execution time
for df in [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]:
    df["transfer+kernel"] = df["data_to_fpga_average"] + df["kernel_average"] + df["data_to_host_average"]
    df["transfer+kernel"] /= 1_000_000 # to miliseconds

bar_width = 0.12
app_names = df_u50_slow["app_name"].values
x = np.arange(len(app_names))

# Total execution time 200 MHz
plt.bar(x - bar_width, df_u50_slow["average"].values, width=bar_width, label=f"U50 HBM")
plt.bar(x            , df_u280_slow["average"].values, width=bar_width, label=f"U280 HBM")
plt.bar(x + bar_width, df_u280_ddr_slow["average"].values, width=bar_width, label=f"U280 DDR")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average total execution time (s)")
plt.legend()
plt.tight_layout()

filename = "execution-time-total-200mhz.png"
print(f"Saving figure to {filename}")
plt.savefig(filename)
plt.clf()

# Total execution time unlimited
plt.bar(x - bar_width, df_u50_fast["average"].values, width=bar_width, label="U50 HBM")
plt.bar(x            , df_u280_fast["average"].values, width=bar_width, label="U280 HBM")
plt.bar(x + bar_width, df_u280_ddr_fast["average"].values, width=bar_width, label="U280 DDR")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average total execution time (s)")
plt.legend()
plt.tight_layout()

filename = "execution-time-total-unlimited.png"
print(f"Saving figure to {filename}")
plt.savefig(filename)
plt.clf()

# Data transfer + kernel time 200 MHz
plt.bar(x - bar_width, df_u50_slow["transfer+kernel"].values, width=bar_width, label=f"U50 HBM")
plt.bar(x            , df_u280_slow["transfer+kernel"].values, width=bar_width, label=f"U280 HBM")
plt.bar(x + bar_width, df_u280_ddr_slow["transfer+kernel"].values, width=bar_width, label=f"U280 DDR")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average data transfer + kernel time (ms)")
# plt.grid(which="both", axis="y")
plt.yscale("log")
plt.legend(loc="upper left")
plt.tight_layout()

filename = "execution-time-transfer-kernel-200mhz.png"
print(f"Saving figure to {filename}")
plt.savefig(filename)
plt.clf()

# Data transfer + kernel time unlimited
plt.bar(x - bar_width, df_u50_fast["transfer+kernel"].values, width=bar_width, label="U50 HBM")
plt.bar(x            , df_u280_fast["transfer+kernel"].values, width=bar_width, label="U280 HBM")
plt.bar(x + bar_width, df_u280_ddr_fast["transfer+kernel"].values, width=bar_width, label="U280 DDR")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average data transfer + kernel time (ms)")
# plt.grid(which="both", axis="y")
plt.yscale("log")
plt.legend(loc="upper left")
plt.tight_layout()

filename = "execution-time-transfer-kernel-unlimited.png"
print(f"Saving figure to {filename}")
plt.savefig(filename)
