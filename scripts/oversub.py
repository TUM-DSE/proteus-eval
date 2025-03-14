#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df_u280_fast = pd.read_csv(f"../data/native/oversub-u280-fast.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv(f"../data/native/oversub-u280-ddr-fast.csv", skipinitialspace=True)
dfs = [df_u280_fast, df_u280_ddr_fast]

# Runs without -o option until this index
unopt_index = 8

bar_width = 0.2
app_names = df_u280_fast["mem_limit"][:unopt_index]
app_names[0] = "unlimited"
x = np.arange(len(app_names))

times_hbm_unopt = df_u280_fast["time_total"][:unopt_index].values
stddev_hbm_unopt = df_u280_fast["time_total_stddev"][:unopt_index].values
times_hbm_opt = df_u280_fast["time_total"][unopt_index:].values
stddev_hbm_opt = df_u280_fast["time_total_stddev"][unopt_index:].values
# Index 0 is no mem limit, no chunking, no optimization
times_hbm_opt = np.insert(times_hbm_opt, 0, 0.0)
stddev_hbm_opt = np.insert(stddev_hbm_opt, 0, 0.0)
hbm_opt_diff = (times_hbm_opt[1:] / times_hbm_unopt[1:] * 100) - 100

times_ddr_unopt = df_u280_ddr_fast["time_total"][:unopt_index].values
stddev_ddr_unopt = df_u280_ddr_fast["time_total_stddev"][:unopt_index].values
times_ddr_opt = df_u280_ddr_fast["time_total"][unopt_index:].values
stddev_ddr_opt = df_u280_ddr_fast["time_total_stddev"][unopt_index:].values
# Index 0 is no mem limit, no chunking, no optimization
times_ddr_opt = np.insert(times_ddr_opt, 0, 0.0)
stddev_ddr_opt = np.insert(stddev_ddr_opt, 0, 0.0)
ddr_opt_diff = (times_ddr_opt[1:] / times_ddr_unopt[1:] * 100) - 100

# HBM unopt
plt.bar(x - 1.5 * bar_width, times_hbm_unopt, width=bar_width, label="HBM sequential")
plt.errorbar(x - 1.5 * bar_width, times_hbm_unopt, yerr=stddev_hbm_unopt, fmt="none", color="k")

# HBM opt
bars = plt.bar(x - 0.5 * bar_width, times_hbm_opt, width=bar_width, label="HBM optimized")
for i, b in enumerate(bars[1:]):
    plt.text(b.get_x() + 0.04, b.get_height() + 0.05,
             f"{hbm_opt_diff[i]:+.2f}%", rotation=90, size=7)
plt.errorbar(x - 0.5 * bar_width, times_hbm_opt, yerr=stddev_hbm_opt, fmt="none", color="k")

# DDR unopt
plt.bar(x + 0.5 * bar_width, times_ddr_unopt, width=bar_width,
        label="DDR sequential, unified memory banks")
plt.errorbar(x + 0.5 * bar_width, times_ddr_unopt, yerr=stddev_ddr_unopt, fmt="none", color="k")

# DDR opt
bars = plt.bar(x + 1.5 * bar_width, times_ddr_opt, width=bar_width,
               label="DDR optimized, unified memory banks")
for i, b in enumerate(bars[1:]):
    plt.text(b.get_x() + 0.04, b.get_height() + 0.05,
             f"{ddr_opt_diff[i]:+.2f}%", rotation=90, size=7)
plt.errorbar(x + 1.5 * bar_width, times_ddr_opt, yerr=stddev_ddr_opt, fmt="none", color="k")

plt.xticks(x, app_names)
plt.xlabel("On-FPGA memory usage (MiB)")
plt.ylabel("Data transfer + kernel time (s)")
plt.legend(loc="lower center")
plt.tight_layout()

filename = f"../plots/native/oversub.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
