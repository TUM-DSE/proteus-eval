#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
import common


def configure_ax():
    ax = plt.gca()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_axisbelow(True)
    ax.grid(axis='y')


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

savefig_args = {
    "dpi": 300,
    "pad_inches": 0.02,
    "bbox_inches": 'tight',
    "format": "pdf",
}

colors = [common.bar_blue, common.bar_blue, common.bar_orange,
          common.bar_orange, common.bar_green, common.bar_green]
hatches = ["", "//"]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

plt.rcParams.update({'font.size': 12})
width = 7.0
aspect = 2
height = width / aspect
plt.figure(figsize=(width, height))

df_u50_slow = pd.read_csv(f"../data/native/u50-slow.csv", skipinitialspace=True)
df_u50_fast = pd.read_csv(f"../data/native/u50-fast.csv", skipinitialspace=True)
df_u280_slow = pd.read_csv(f"../data/native/u280-slow.csv", skipinitialspace=True)
df_u280_fast = pd.read_csv(f"../data/native/u280-fast.csv", skipinitialspace=True)
df_u280_ddr_slow = pd.read_csv(f"../data/native/u280-ddr-slow.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv(f"../data/native/u280-ddr-fast.csv", skipinitialspace=True)

# Data frames containing only apps selected for the plot
df_u50_slow_sel = pd.DataFrame()
df_u50_fast_sel = pd.DataFrame()
df_u280_slow_sel = pd.DataFrame()
df_u280_fast_sel = pd.DataFrame()
df_u280_ddr_slow_sel = pd.DataFrame()
df_u280_ddr_fast_sel = pd.DataFrame()

sel_apps = ["cl_burst_rw", "cl_helloworld", "cl_gmem_2banks",
            "cl_wide_mem_rw_strm", "cl_wide_mem_rw_2x"]

dfs = [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]
dfs_sel = [df_u50_slow_sel, df_u50_fast_sel, df_u280_slow_sel,
           df_u280_fast_sel, df_u280_ddr_slow_sel, df_u280_ddr_fast_sel]
labels = ["U50 HBM 200/300 MHz", "U50 HBM unlimited", "U280 HBM 200/300 MHz",
          "U280 HBM unlimited", "U280 DDR 200/300 MHz", "U280 DDR unlimited"]

# Sum up data transfer + kernel execution time,
# time_cpu seems to be measured incorrectly for Proteus currently.
# Also set selected apps.
for i in range(len(dfs)):
    dfs[i]["transfer+kernel"] = dfs[i]["data_to_fpga_ocl"] + \
        dfs[i]["kernel_ocl"] + dfs[i]["data_to_host_ocl"]
    # Average standard deviation is the square root of the average variance, variance is stddev ** 2
    avg_variance = (dfs[i]["data_to_fpga_ocl_stddev"] ** 2 + dfs[i]
                    ["kernel_ocl_stddev"] ** 2 + dfs[i]["data_to_host_ocl_stddev"] ** 2) / 3
    dfs[i]["transfer+kernel_stddev"] = np.sqrt(avg_variance)

    dfs_sel[i] = dfs[i][(dfs[i]["app_name"] == sel_apps[0]) | (dfs[i]["app_name"] == sel_apps[1]) |
                        (dfs[i]["app_name"] == sel_apps[2]) | (dfs[i]["app_name"] == sel_apps[3]) |
                        (dfs[i]["app_name"] == sel_apps[4])]

app_names = sel_apps
# Remove cl_
app_names = [s[3:] for s in app_names]
# Remove _strm
for i in range(len(app_names)):
    if app_names[i] == "wide_mem_rw_strm":
        app_names[i] = "wide_mem_rw"

x = np.arange(len(app_names))

# Total execution time ----------------------------------------------------------------------------------

for i in range(6):
    x_offs = i - 2
    plt.bar(x + x_offs * bar_width, dfs_sel[i]["average"].values,
            hatch=hatches[i % 2], label=labels[i], **bar_args)
    plt.errorbar(x + x_offs * bar_width, dfs_sel[i]["average"].values,
                 yerr=dfs_sel[i]["stddev"].values, **errorbar_args)

plt.xticks(x, app_names, rotation=10)
plt.ylabel("Total execution time (s)")
plt.legend(loc='upper left', fancybox=True, shadow=True,
           fontsize=8, ncol=1, bbox_to_anchor=(0, 0.98))
plt.tight_layout()
configure_ax()

filename = f"../plots/native/time-motivation-total.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, **savefig_args)
plt.clf()

# Data transfer + kernel time ---------------------------------------------------------------------------

for i in range(6):
    x_offs = i - 2
    plt.bar(x + x_offs * bar_width, dfs_sel[i]["transfer+kernel"].values,
            hatch=hatches[i % 2], label=labels[i], **bar_args)
    plt.errorbar(x + x_offs * bar_width, dfs_sel[i]["transfer+kernel"].values,
                 yerr=dfs_sel[i]["transfer+kernel_stddev"].values, **errorbar_args)

plt.xticks(x, app_names, rotation=10)
plt.ylabel("Data transfer + kernel time (s)")
plt.legend(loc='upper left', fancybox=True, shadow=True,
           fontsize=8, ncol=1, bbox_to_anchor=(0, 0.98))
plt.tight_layout()
configure_ax()

filename = f"../plots/native/time-motivation-fpga.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, **savefig_args)
plt.clf()
