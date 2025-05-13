#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import common

bar_width = 0.13

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

savefig_args = {
    "dpi": 300,
    "pad_inches": 0.02,
    "bbox_inches": 'tight',
    "format": "pdf",
}

colors = [common.bar_blue, common.bar_blue, common.bar_blue,
          common.bar_orange, common.bar_orange, common.bar_orange]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

plt.rcParams.update({'font.size': 10})
width = 4.0
height = 2.8
plt.figure(figsize=(width, height))

# First 10 rows compute intensive applications, remaining rows memory intensive applications
df_u280_hbm = pd.read_csv(f"../data/native/memory-u280-300mhz.csv")
df_u280_ddr = pd.read_csv(f"../data/native/memory-u280-ddr-300mhz.csv")

# Native vs Proteus plot ------------------------------------------------------------------------------------

xlabels = ["wmem2x", "wmem4x"]

x = np.arange(len(xlabels))

plt.bar(x - 2.5 * bar_width, df_u280_hbm["time_loop"].loc[[0, 3]],
        label="HBM default", **bar_args)
plt.errorbar(x - 2.5 * bar_width, df_u280_hbm["time_loop"].loc[[0, 3]],
             yerr=df_u280_hbm["time_loop_stddev"].loc[[0, 3]], **errorbar_args)
plt.bar(x - 1.5 * bar_width, df_u280_hbm["time_loop"].loc[[1, 4]],
        label="HBM bank-opt", hatch="//", **bar_args)
plt.errorbar(x - 1.5 * bar_width, df_u280_hbm["time_loop"].loc[[1, 4]],
             yerr=df_u280_hbm["time_loop_stddev"].loc[[1, 4]], **errorbar_args)
plt.bar(x - 0.5 * bar_width, df_u280_hbm["time_loop"].loc[[2, 5]],
        label="HBM bank-opt+stream", hatch="**", **bar_args)
plt.errorbar(x - 0.5 * bar_width, df_u280_hbm["time_loop"].loc[[2, 5]],
             yerr=df_u280_hbm["time_loop_stddev"].loc[[2, 5]], **errorbar_args)

plt.bar(x + 0.5 * bar_width, df_u280_ddr["time_loop"].loc[[0, 3]],
        label="DDR default", **bar_args)
plt.errorbar(x + 0.5 * bar_width, df_u280_ddr["time_loop"].loc[[0, 3]],
             yerr=df_u280_ddr["time_loop_stddev"].loc[[0, 3]], **errorbar_args)
plt.bar(x + 1.5 * bar_width, df_u280_ddr["time_loop"].loc[[1, 4]],
        label="DDR bank-opt", hatch="//", **bar_args)
plt.errorbar(x + 1.5 * bar_width, df_u280_ddr["time_loop"].loc[[1, 4]],
             yerr=df_u280_ddr["time_loop_stddev"].loc[[1, 4]], **errorbar_args)
plt.bar(x + 2.5 * bar_width, df_u280_ddr["time_loop"].loc[[2, 5]],
        label="DDR bank-opt+stream", hatch="**", **bar_args)
plt.errorbar(x + 2.5 * bar_width, df_u280_ddr["time_loop"].loc[[2, 5]],
             yerr=df_u280_ddr["time_loop_stddev"].loc[[2, 5]], **errorbar_args)

plt.xticks(x, xlabels, rotation=0)
plt.ylim(0, 11)
plt.ylabel("Data transfer + kernel time (s)")
# x_margin, y_margin = plt.margins()
# plt.margins(y=y_margin + 0.15)
plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=2,
           prop={'size': 8}, bbox_to_anchor=(-0.1, 1.18))
plt.tight_layout()

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis='y')

filename = f"../plots/time-memory-total.pdf"
print(f"Saving figure to {filename}")
plt.margins(x=0.01, tight=True)
plt.savefig(filename, **savefig_args)
plt.clf()
