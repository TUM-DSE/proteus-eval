#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import common


df = pd.read_csv(f"../data/overheads.csv", skipinitialspace=True)

times = pd.DataFrame()
times["unikernel_boot"] = df["unikernel_boot"]
times["worker_init"] = df["worker_init"]
times["buf_alloc"] = df["buf_alloc"]
times["kernel_create"] = df["kernel_alloc"] + df["kernel_setarg"]
# CPU timer - ocl profiling timer = host overhead
times["kernel_exec"] = (df["kernel_enqueue"] + df["init_transfer"] + 2 * df["transfer"]) - \
    (df["data_to_fpga_time_ocl"] + df["kernel_time_ocl"] + df["data_to_host_time_ocl"])
times["finish"] = df["finish"]
print(times)
# times = df[["kernel_alloc", "kernel_setarg", "kernel_enqueue", "buf_alloc", "transfer", "finish"]]
# times_stddevs = df[["kernel_alloc_stddev", "kernel_setarg_stddev",
#                     "kernel_enqueue_stddev", "buf_alloc_stddev", "transfer_stddev", "finish_stddev"]]

bar_width = 0.14

bar_args = {
    "width": bar_width,
    "linewidth": 1,
    "edgecolor": "k",
}

# errorbar_args = {
#     "fmt": "none",
#     "color": "k",
#     "elinewidth": 1,
#     "capsize": 2,
# }

colors = [common.bar_blue, common.bar_blue, common.bar_orange,
          common.bar_orange, common.bar_green, common.bar_green]
hatches = ["", "//"]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

plt.rcParams.update({'font.size': 9})
width = 4.2
height = 3.0
# width = 7.0
# aspect = 2.0
# height = width / aspect
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(width, height))

ax1.set_ylim(70, 450)
ax2.set_ylim(1, 24)
ax3.set_ylim(0, 0.01)

# Hide the spines between plots
ax1.spines.bottom.set_visible(False)
ax2.spines.top.set_visible(False)
ax2.spines.bottom.set_visible(False)
ax3.spines.top.set_visible(False)

# Hide top spine
ax1.spines.top.set_visible(False)

# Hide the x axis from the upper plots
ax1.get_xaxis().set_visible(False)
ax2.get_xaxis().set_visible(False)

d = .5  # Proportion of vertical to horizontal extent of the slanted line
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=10,
              linestyle="none", color='k', mec='k', mew=2, clip_on=False)
ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)
ax2.plot([0, 1], [0, 0], transform=ax2.transAxes, **kwargs)
ax3.plot([0, 1], [1, 1], transform=ax3.transAxes, **kwargs)

# x_labels = ["Boot unikernel", "Init platform",
#             "Create buffers", "Create kernel", "Exec kernel", "Sync"]
x_labels = ["Boot\nOS", "Init\nplatform",
            "Create\nbuffers", "Create\nkernel", "Execute", "Sync"]
x = np.arange(len(x_labels))

axs = [ax1, ax2, ax3]

for ax in axs:
    ax.bar(x - 2.5 * bar_width, times.iloc[3], hatch=hatches[0], label="U50 native", **bar_args)
    ax.bar(x - 1.5 * bar_width, times.iloc[0], hatch=hatches[1], label="U50 Proteus", **bar_args)
    ax.bar(x - 0.5 * bar_width, times.iloc[4], hatch=hatches[0], label="U280 native", **bar_args)
    ax.bar(x + 0.5 * bar_width, times.iloc[1], hatch=hatches[1], label="U280 Proteus", **bar_args)
    ax.bar(x + 1.5 * bar_width, times.iloc[5], hatch=hatches[0], label="U280-DDR native", **bar_args)
    ax.bar(x + 2.5 * bar_width, times.iloc[2], hatch=hatches[1], label="U280-DDR Proteus", **bar_args)

plt.xticks(x, x_labels, rotation=0)
ax2.set_ylabel("Time (ms)")
# ax2.yaxis.set_label_coords(-0.07, 0.7)
ax2.yaxis.set_label_coords(-0.09, 0.7)
ax1.legend(loc='upper right', fancybox=True, shadow=True,
           ncol=3, prop={'size': 7.5}, bbox_to_anchor=(1, 1.7))
plt.tight_layout()
# FIXME: plt.margiins() doesn't change margins for some reason...
plt.margins(x=0.0, tight=True) 
plt.subplots_adjust(wspace=0, hspace=0.05)

for ax in axs:
    ax.set_axisbelow(True)
    ax.yaxis.grid()

# ax.spines['top'].set_visible(False)
# ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
# ax.spines['left'].set_visible(False)
# ax.set_axisbelow(True)
# ax.grid(axis='y')

filename = f"../plots/overheads.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, dpi=300, pad_inches=0.02, bbox_inches='tight', format="pdf")
