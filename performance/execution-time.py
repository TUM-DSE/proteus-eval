#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_u50_300mhz = pd.read_csv("../data/u50-perf-300mhz.csv", skipinitialspace=True)
df_u280_300mhz = pd.read_csv("../data/u280-perf-300mhz.csv", skipinitialspace=True)
df_u50_faster = pd.read_csv("../data/u50-perf-faster.csv", skipinitialspace=True)
df_u280_faster = pd.read_csv("../data/u280-perf-faster.csv", skipinitialspace=True)
df_u280_ddr_300mhz = pd.read_csv("../data/u280-perf-ddr-300mhz.csv", skipinitialspace=True)

bar_width = 0.15
app_names = df_u50_300mhz["app_name"].values
x = np.arange(len(app_names))

plt.bar(x - 2 * bar_width, df_u50_300mhz["average"].values, width=bar_width, label="U50 300MHz")
plt.bar(x - bar_width, df_u280_300mhz["average"].values, width=bar_width, label="U280 300MHz")
plt.bar(x, df_u50_faster["average"].values, width=bar_width, label="U50 faster")
plt.bar(x + bar_width, df_u280_faster["average"].values, width=bar_width, label="U280 faster")
plt.bar(x + 2 * bar_width, df_u280_ddr_300mhz["average"].values, width=bar_width, label="U280 DDR 300MHz")

plt.xticks(x, app_names, rotation=45, ha="right")
plt.ylabel("Average time (s)")
plt.legend()
plt.tight_layout()

plt.savefig("execution-time.png")
