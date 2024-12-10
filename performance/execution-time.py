#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_u50_slow = pd.read_csv("../data/u50-slow.csv", skipinitialspace=True)
df_u280_slow = pd.read_csv("../data/u280-slow.csv", skipinitialspace=True)
df_u50_fast = pd.read_csv("../data/u50-fast.csv", skipinitialspace=True)
df_u280_fast = pd.read_csv("../data/u280-fast.csv", skipinitialspace=True)
df_u280_ddr_slow = pd.read_csv("../data/u280-ddr-slow.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv("../data/u280-ddr-fast.csv", skipinitialspace=True)

bar_width = 0.1
app_names = df_u50_slow["app_name"].values
x = np.arange(len(app_names))

plt.bar(x - 2 * bar_width, df_u50_slow["average"].values, width=bar_width, label="U50 slow")
plt.bar(x - bar_width, df_u280_slow["average"].values, width=bar_width, label="U280 slow")
plt.bar(x, df_u50_fast["average"].values, width=bar_width, label="U50 fast")
plt.bar(x + bar_width, df_u280_fast["average"].values, width=bar_width, label="U280 fast")
plt.bar(x + 2 * bar_width, df_u280_ddr_slow["average"].values, width=bar_width, label="U280 DDR slow")
plt.bar(x + 3 * bar_width, df_u280_ddr_fast["average"].values, width=bar_width, label="U280 DDR fast")

plt.xticks(x, app_names, rotation=45, ha="right")
plt.ylabel("Average time (s)")
# plt.yscale("log")
plt.legend()
plt.tight_layout()

filename = "execution-time.png"
print(f"Saving figure to {filename}")
plt.savefig(filename)
