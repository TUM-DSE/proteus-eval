#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import common


df = pd.read_csv(f"../data/overheads.csv", skipinitialspace=True)
times = df[["kernel_alloc", "kernel_setarg", "kernel_enqueue", "buf_alloc", "transfer", "finish"]]
times_stddevs = df[["kernel_alloc_stddev", "kernel_setarg_stddev",
                    "kernel_enqueue_stddev", "buf_alloc_stddev", "transfer_stddev", "finish_stddev"]]

bar_width = 0.12

bar_args = {
    "width": bar_width,
    "linewidth": 1,
    "edgecolor": "k",
}

errorbar_args = {
    "fmt": "none",
    "color": "k",
    "elinewidth": 1,
    "capsize": 2,
}

colors = [common.bar_blue, common.bar_blue, common.bar_orange,
          common.bar_orange, common.bar_green, common.bar_green]
hatches = ["", "//"]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

plt.rcParams.update({'font.size': 12})
width = 7.0
aspect = 2.0
height = width / aspect
plt.figure(figsize=(width, height))

x_labels = ["Allocate kernel", "Set kernel args",
            "Enqueue kernel", "Allocate buffer", "Data transfer", "Finish"]
x = np.arange(len(x_labels))

plt.bar(x - 2.5 * bar_width, times.iloc[3], hatch=hatches[0], label="Native U50", **bar_args)
plt.errorbar(x - 2.5 * bar_width, times.iloc[3], yerr=times_stddevs.iloc[3], **errorbar_args)

plt.bar(x - 1.5 * bar_width, times.iloc[0], hatch=hatches[1], label="Proteus U50", **bar_args)
plt.errorbar(x - 1.5 * bar_width, times.iloc[0], yerr=times_stddevs.iloc[0], **errorbar_args)

plt.bar(x - 0.5 * bar_width, times.iloc[4], hatch=hatches[0], label="Native U280 HBM", **bar_args)
plt.errorbar(x - 0.5 * bar_width, times.iloc[4], yerr=times_stddevs.iloc[4], **errorbar_args)

plt.bar(x + 0.5 * bar_width, times.iloc[1], hatch=hatches[1], label="Proteus U280 HBM", **bar_args)
plt.errorbar(x + 0.5 * bar_width, times.iloc[1], yerr=times_stddevs.iloc[1], **errorbar_args)

plt.bar(x + 1.5 * bar_width, times.iloc[5], hatch=hatches[0], label="Native U280 DDR", **bar_args)
plt.errorbar(x + 1.5 * bar_width, times.iloc[5], yerr=times_stddevs.iloc[5], **errorbar_args)

plt.bar(x + 2.5 * bar_width, times.iloc[2], hatch=hatches[1], label="Proteus U280 DDR", **bar_args)
plt.errorbar(x + 2.5 * bar_width, times.iloc[2], yerr=times_stddevs.iloc[2], **errorbar_args)

plt.xticks(x, x_labels, rotation=15)
plt.ylabel("Time (ms)")
plt.yscale("log")
plt.legend(loc='upper right', fancybox=True, shadow=True, ncol=2, fontsize=8, bbox_to_anchor=(1, 1))
plt.tight_layout()

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis='y')

filename = f"../plots/overheads.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, dpi=300, pad_inches=0.02, bbox_inches='tight', format="pdf")
