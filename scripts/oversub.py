#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import common


bar_width = 0.15

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
          common.bar_orange, common.bar_orange]
hatches = ["", "//", "--"]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

plt.rcParams.update({'font.size': 12})
width = 7.0
aspect = 2
height = width / aspect
plt.figure(figsize=(width, height))

df_u280_fast = pd.read_csv(f"../data/native/oversub-u280-fast.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv(f"../data/native/oversub-u280-ddr-fast.csv", skipinitialspace=True)
df_u280_ddr_dc_fast = pd.read_csv(
    f"../data/native/oversub-u280-ddr-dualchannel-fast.csv", skipinitialspace=True)
dfs = [df_u280_fast, df_u280_ddr_fast]

# Runs for HBM and DDR without -o option until this index, DDR dual channel always uses -o option
unopt_end = 6

app_names = df_u280_fast["mem_limit"][:unopt_end]
app_names[0] = "unlimited"
x = np.arange(len(app_names))

times_hbm_unopt = df_u280_fast["time_total"][:unopt_end].values
stddev_hbm_unopt = df_u280_fast["time_total_stddev"][:unopt_end].values
times_hbm_opt = df_u280_fast["time_total"][unopt_end:].values
stddev_hbm_opt = df_u280_fast["time_total_stddev"][unopt_end:].values
# Index 0 is no mem limit, no chunking, no optimization
times_hbm_opt = np.insert(times_hbm_opt, 0, 0.0)
stddev_hbm_opt = np.insert(stddev_hbm_opt, 0, 0.0)
hbm_opt_diff = (times_hbm_opt[1:] / times_hbm_unopt[1:] * 100) - 100

times_ddr_unopt = df_u280_ddr_fast["time_total"][:unopt_end].values
stddev_ddr_unopt = df_u280_ddr_fast["time_total_stddev"][:unopt_end].values
times_ddr_opt = df_u280_ddr_fast["time_total"][unopt_end:].values
stddev_ddr_opt = df_u280_ddr_fast["time_total_stddev"][unopt_end:].values
# Index 0 is no mem limit, no chunking, no optimization
times_ddr_opt = np.insert(times_ddr_opt, 0, 0.0)
stddev_ddr_opt = np.insert(stddev_ddr_opt, 0, 0.0)
ddr_opt_diff = (times_ddr_opt[1:] / times_ddr_unopt[1:] * 100) - 100

times_ddr_dc = df_u280_ddr_dc_fast["time_total"].values
stddev_ddr_dc = df_u280_ddr_dc_fast["time_total_stddev"].values
# Index 0 is no mem limit, no chunking, no optimization
times_ddr_dc = np.insert(times_ddr_dc, 0, 0.0)
stddev_ddr_dc = np.insert(stddev_ddr_dc, 0, 0.0)
ddr_dc_diff = (times_ddr_dc[1:] / times_ddr_opt[1:] * 100) - 100

# HBM unopt
plt.bar(x - 1.5 * bar_width, times_hbm_unopt, hatch=hatches[0], label="HBM seq", **bar_args)
plt.errorbar(x - 1.5 * bar_width, times_hbm_unopt, yerr=stddev_hbm_unopt, **errorbar_args)

# HBM opt
bars = plt.bar(x - 0.5 * bar_width, times_hbm_opt,
               hatch=hatches[1], label="HBM opt", **bar_args)
for i, b in enumerate(bars[1:]):
    plt.text(b.get_x() + 0.03, b.get_height() + 0.05,
             f"{hbm_opt_diff[i]:+.2f}%", rotation=90, size=7)
plt.errorbar(x - 0.5 * bar_width, times_hbm_opt, yerr=stddev_hbm_opt, **errorbar_args)

# DDR unopt
plt.bar(x + 0.5 * bar_width, times_ddr_unopt,
        hatch=hatches[0], label="DDR seq", **bar_args)
plt.errorbar(x + 0.5 * bar_width, times_ddr_unopt, yerr=stddev_ddr_unopt, **errorbar_args)

# DDR opt
# bars = plt.bar(x + 1 * bar_width, times_ddr_opt, hatch=hatches[1],
#                label="DDR opt", **bar_args)
# for i, b in enumerate(bars[1:]):
#     plt.text(b.get_x() + 0.03, b.get_height() + 0.05,
#              f"{ddr_opt_diff[i]:+.2f}%", rotation=90, size=7)
# plt.errorbar(x + 1 * bar_width, times_ddr_opt, yerr=stddev_ddr_opt, **errorbar_args)

# DDR opt + dualchannel
bars = plt.bar(x + 1.5 * bar_width, times_ddr_dc, hatch=hatches[1],
               label="DDR opt", **bar_args)
for i, b in enumerate(bars[1:]):
    plt.text(b.get_x() + 0.03, b.get_height() + 0.05,
             f"{ddr_dc_diff[i]:+.2f}%", rotation=90, size=7)
plt.errorbar(x + 1.5 * bar_width, times_ddr_dc, yerr=stddev_ddr_dc, **errorbar_args)

plt.xticks(x, app_names)
plt.xlabel("Emulated FPGA memory capacity (MiB)")
plt.ylabel("Data transfer + kernel time (s)")
x_margin, y_margin = plt.margins()
plt.margins(y=y_margin + 0.1)
plt.legend(loc="upper left", fancybox=True, shadow=True,
           ncol=4, fontsize=8, bbox_to_anchor=(0, 1))
plt.tight_layout()

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis='y')

filename = f"../plots/native/oversub.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, dpi=300, pad_inches=0.02, bbox_inches='tight', format="pdf")
