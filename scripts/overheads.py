#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv(f"../data/overheads.csv", skipinitialspace=True)
times = df[["kernel_alloc", "kernel_setarg", "kernel_enqueue", "buf_alloc", "transfer", "finish"]]
times_stddevs = df[["kernel_alloc_stddev", "kernel_setarg_stddev",
                    "kernel_enqueue_stddev", "buf_alloc_stddev", "transfer_stddev", "finish_stddev"]]

bar_width = 0.12
x_labels = ["Allocate kernel", "Set kernel args", "Enqueue kernel", "Allocate buffer", "Data transfer", "Finish"]
x = np.arange(len(x_labels))

plt.bar(x - 2.5 * bar_width, times.iloc[0], width=bar_width, label="Proteus U50")
plt.errorbar(x - 2.5 * bar_width, times.iloc[0], yerr=times_stddevs.iloc[0], fmt="none", color="k")

plt.bar(x - 1.5 * bar_width, times.iloc[3], width=bar_width, label="Native U50")
plt.errorbar(x - 1.5 * bar_width, times.iloc[3], yerr=times_stddevs.iloc[3], fmt="none", color="k")

plt.bar(x - 0.5 * bar_width, times.iloc[1], width=bar_width, label="Proteus U280 HBM")
plt.errorbar(x - 0.5 * bar_width, times.iloc[1], yerr=times_stddevs.iloc[1], fmt="none", color="k")

plt.bar(x + 0.5 * bar_width, times.iloc[4], width=bar_width, label="Native U280 HBM")
plt.errorbar(x + 0.5 * bar_width, times.iloc[4], yerr=times_stddevs.iloc[4], fmt="none", color="k")

plt.bar(x + 1.5 * bar_width, times.iloc[2], width=bar_width, label="Proteus U280 DDR")
plt.errorbar(x + 1.5 * bar_width, times.iloc[2], yerr=times_stddevs.iloc[2], fmt="none", color="k")

plt.bar(x + 2.5 * bar_width, times.iloc[5], width=bar_width, label="Native U280 DDR")
plt.errorbar(x + 2.5 * bar_width, times.iloc[5], yerr=times_stddevs.iloc[5], fmt="none", color="k")

plt.xticks(x, x_labels, rotation=30, ha="right")
plt.ylabel("Time (ms)")
plt.yscale("log")
plt.legend()
plt.tight_layout()

filename = f"../plots/overheads.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
