#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


df_u280_fast = pd.read_csv(f"../data/native/oversub-u280-fast.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv(f"../data/native/oversub-u280-ddr-fast.csv", skipinitialspace=True)
dfs = [df_u280_fast, df_u280_ddr_fast]

# Runs without -o option until this index
unopt_index = 7

bar_width = 0.2
app_names = df_u280_fast["mem_limit"][:unopt_index]
app_names[0] = "unlimited"
x = np.arange(len(app_names))

times_hbm_unopt = df_u280_fast["time_total"][:unopt_index].values
times_hbm_opt = df_u280_fast["time_total"][unopt_index:].values
times_hbm_opt = np.insert(times_hbm_opt, 0, 0.0)  # Index 0 is unlimited mem limit

times_ddr_unopt = df_u280_ddr_fast["time_total"][:unopt_index].values
times_ddr_opt = df_u280_ddr_fast["time_total"][unopt_index:].values
times_ddr_opt = np.insert(times_ddr_opt, 0, 0.0)  # Index 0 is unlimited mem limit

plt.bar(x - 2 * bar_width, times_hbm_unopt, width=bar_width, label="HBM sequential")
plt.bar(x - 1 * bar_width, times_hbm_opt, width=bar_width, label="HBM optimized")
plt.bar(x + 0 * bar_width, times_ddr_unopt, width=bar_width, label="DDR sequential")
plt.bar(x + 1 * bar_width, times_ddr_opt, width=bar_width, label="DDR optimized")

plt.xticks(x, app_names)
plt.xlabel("On-FPGA memory limit (MiB)")
plt.ylabel("Data transfer + kernel time (s)")
plt.legend()
plt.tight_layout()

filename = f"../plots/native/oversub.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
