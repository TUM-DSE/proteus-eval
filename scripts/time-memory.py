#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_u50_slow = {}
df_u50_fast = {}
df_u280_slow = {}
df_u280_fast = {}
df_u280_ddr_slow = {}
df_u280_ddr_fast = {}

# Individual plots ----------------------------------------------------------------------------------------------------

for setting in ["native", "proteus"]:

    # First 10 rows compute intensive applications, remaining rows memory intensive applications
    df_u50_slow[setting] = pd.read_csv(f"../data/{setting}/u50-slow.csv", skipinitialspace=True).iloc[10:]
    df_u50_fast[setting] = pd.read_csv(f"../data/{setting}/u50-fast.csv", skipinitialspace=True).iloc[10:]
    df_u280_slow[setting] = pd.read_csv(f"../data/{setting}/u280-slow.csv", skipinitialspace=True).iloc[10:]
    df_u280_fast[setting] = pd.read_csv(f"../data/{setting}/u280-fast.csv", skipinitialspace=True).iloc[10:]
    df_u280_ddr_slow[setting] = pd.read_csv(f"../data/{setting}/u280-ddr-slow.csv", skipinitialspace=True).iloc[10:]
    df_u280_ddr_fast[setting] = pd.read_csv(f"../data/{setting}/u280-ddr-fast.csv", skipinitialspace=True).iloc[10:]

    dfs = [df_u50_slow, df_u280_slow, df_u280_ddr_slow, df_u50_fast, df_u280_fast, df_u280_ddr_fast]
    labels = ["U50 HBM 200 MHz", "U280 HBM 200 MHz", "U280 DDR 200 MHz", "U50 HBM unlimited", "U280 HBM unlimited", "U280 DDR unlimited"]

    # Sum up data transfer + kernel execution time, time_cpu seems to be measured incorrectly for Proteus currently
    for df in dfs:
        df[setting]["transfer+kernel"] = df[setting]["data_to_fpga_ocl"] + df[setting]["kernel_ocl"] + df[setting]["data_to_host_ocl"]
        # Average standard deviation is the square root of the average variance, variance is stddev ** 2
        avg_variance = (df[setting]["data_to_fpga_ocl_stddev"] ** 2 + df[setting]["kernel_ocl_stddev"] ** 2 + df[setting]["data_to_host_ocl_stddev"] ** 2) / 3
        df[setting]["transfer+kernel_stddev"] = np.sqrt(avg_variance)

    bar_width = 0.12
    app_names = df_u50_slow[setting]["app_name"].values
    x = np.arange(len(app_names))

    # Total execution time --------------------------------------------------------------------------------------

    for i in range(6):
        x_offs = i - 2
        plt.bar(x + x_offs * bar_width, dfs[i][setting]["average"].values, width=bar_width, label=labels[i])
        plt.errorbar(x + x_offs * bar_width, dfs[i][setting]["average"].values, yerr=dfs[i][setting]["stddev"].values, fmt="none", color="k")

    plt.xticks(x, app_names, rotation=20)
    plt.ylabel("Total execution time (s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/time-memory-total.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

    # Data transfer + kernel time -------------------------------------------------------------------------------

    for i in range(6):
        x_offs = i - 2
        plt.bar(x + x_offs * bar_width, dfs[i][setting]["transfer+kernel"].values, width=bar_width, label=labels[i])
        plt.errorbar(x + x_offs * bar_width, dfs[i][setting]["transfer+kernel"].values, yerr=dfs[i][setting]["transfer+kernel_stddev"].values, fmt="none", color="k")

    plt.xticks(x, app_names, rotation=20)
    plt.ylabel("Total data transfer + kernel time (s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/time-memory-fpga.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

# Native vs Proteus plot ---------------------------------------------------------------------------------------------

bar_width = 0.12
app_names = df_u50_slow[setting]["app_name"].values
x = np.arange(len(app_names))
dfs = [df_u50_fast, df_u280_fast, df_u280_ddr_fast]
labels = ["U50 HBM native", "U50 HBM Proteus", "U280 HBM native", "U280 HBM Proteus", "U280 DDR native", "U280 DDR Proteus"]

# Total execution time --------------------------------------------------------------------------------------

x_offs = -2
for i in range(3):
    # Native
    plt.bar(x + x_offs * bar_width, dfs[i]["native"]["average"].values, width=bar_width, label=labels[2 * i])
    plt.errorbar(x + x_offs * bar_width, dfs[i]["native"]["average"].values, yerr=dfs[i]["native"]["stddev"].values, fmt="none", color="k")
    x_offs += 1
    # Proteus
    bars = plt.bar(x + x_offs * bar_width, dfs[i]["proteus"]["average"].values, width=bar_width, label=labels[2 * i + 1])
    proteus_overhead = ((dfs[i]["proteus"]["average"].values / dfs[i]["native"]["average"].values) * 100) - 100
    for j, b in enumerate(bars):
        plt.text(b.get_x() + bar_width / 4, b.get_height() + 0.5, f"{proteus_overhead[j]:+.2f}%", rotation=90, size=5)
    plt.errorbar(x + x_offs * bar_width, dfs[i]["proteus"]["average"].values, yerr=dfs[i]["proteus"]["stddev"].values, fmt="none", color="k")
    x_offs += 1

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Total execution time (s)")
plt.legend()
plt.tight_layout()

filename = f"../plots/time-memory-total.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
plt.clf()

# Data transfer + kernel time -------------------------------------------------------------------------------

x_offs = -2
for i in range(3):
    # Native
    plt.bar(x + x_offs * bar_width, dfs[i]["native"]["transfer+kernel"].values, width=bar_width, label=labels[2 * i])
    plt.errorbar(x + x_offs * bar_width, dfs[i]["native"]["transfer+kernel"].values, yerr=dfs[i]["native"]["transfer+kernel_stddev"].values, fmt="none", color="k")
    x_offs += 1
    # Proteus
    bars = plt.bar(x + x_offs * bar_width, dfs[i]["proteus"]["transfer+kernel"].values, width=bar_width, label=labels[2 * i + 1])
    proteus_overhead = ((dfs[i]["proteus"]["transfer+kernel"].values / dfs[i]["native"]["transfer+kernel"].values) * 100) - 100
    for j, b in enumerate(bars):
        plt.text(b.get_x() + bar_width / 4, b.get_height() + 0.2, f"{proteus_overhead[j]:+.2f}%", rotation=90, size=5)
    plt.errorbar(x + x_offs * bar_width, dfs[i]["proteus"]["transfer+kernel"].values, yerr=dfs[i]["proteus"]["transfer+kernel_stddev"].values, fmt="none", color="k")
    x_offs += 1

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Total data transfer + kernel time (s)")
plt.legend()
plt.tight_layout()

filename = f"../plots/time-memory-fpga.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
plt.clf()
