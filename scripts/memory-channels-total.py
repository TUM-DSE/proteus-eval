#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_total_time = pd.read_csv("../data/memory-channels.csv", skipinitialspace=True)

configs = ["singlechannel-300mhz", "multichannel-300mhz", "singlechannel-fast", "multichannel-fast",
           "singlechannel-ddr-300mhz", "singlechannel-ddr-fast", "multichannel-ddr-300mhz", "multichannel-ddr-fast"]

bar_width = 0.25
app_names = df_total_time["app_name"].values
x = np.arange(len(df_total_time))


plt.bar(x, df_total_time["average"].values, width=bar_width)

plt.xticks(x, app_names, rotation=45, ha="right")
plt.ylabel("Average time (s)")
plt.tight_layout()

filename = "../plots/memory-channels-total.png"
print(f"Saving figure to {filename}")
plt.savefig(filename)
