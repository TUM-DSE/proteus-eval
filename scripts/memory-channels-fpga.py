#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_kernel_time = pd.read_csv("../data/memory-channels-kernel.csv", skipinitialspace=True)

configs = ["singlechannel-300mhz", "multichannel-300mhz", "singlechannel-fast", "multichannel-fast",
           "singlechannel-ddr-300mhz", "singlechannel-ddr-fast", "multichannel-ddr-300mhz", "multichannel-ddr-fast"]

bar_width = 0.2
app_names = df_kernel_time["app_name"].values
x = np.arange(len(df_kernel_time))

plt.bar(x - bar_width, df_kernel_time["kernel_avg_time"].values, width=bar_width, label="kernel")
plt.bar(x, df_kernel_time["data_to_fpga_avg_time"].values, width=bar_width, label="data to fpga")
plt.bar(x + bar_width, df_kernel_time["data_to_host_avg_time"].values, width=bar_width, label="data to host")

plt.xticks(x, app_names, rotation=45, ha="right")
plt.ylabel("Average time (ns)")
# plt.ylim(top=12528700)
plt.legend()
plt.tight_layout()

filename = "../plots/memory-channels-fpga.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
