#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import common

def configure_ax():
    ax = plt.gca()

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_axisbelow(True)
    ax.grid(axis='y')

df_u50_slow = {}
df_u50_fast = {}
df_u280_slow = {}
df_u280_fast = {}
df_u280_ddr_slow = {}
df_u280_ddr_fast = {}

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

colors = [common.bar_blue, common.bar_blue, common.bar_orange,
          common.bar_orange, common.bar_green, common.bar_green]
hatches = ["", "//"]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

plt.rcParams.update({'font.size': 10})
width = 4.0
height = 2.8
plt.figure(figsize=(width, height))

# Individual plots ------------------------------------------------------------------------------------------

for setting in ["native", "proteus"]:

    # First 10 rows compute intensive applications, remaining rows memory intensive applications
    df_u50_slow[setting] = pd.read_csv(
        f"../data/{setting}/u50-slow.csv", skipinitialspace=True).iloc[10:]
    df_u50_fast[setting] = pd.read_csv(
        f"../data/{setting}/u50-fast.csv", skipinitialspace=True).iloc[10:]
    df_u280_slow[setting] = pd.read_csv(
        f"../data/{setting}/u280-slow.csv", skipinitialspace=True).iloc[10:]
    df_u280_fast[setting] = pd.read_csv(
        f"../data/{setting}/u280-fast.csv", skipinitialspace=True).iloc[10:]
    df_u280_ddr_slow[setting] = pd.read_csv(
        f"../data/{setting}/u280-ddr-slow.csv", skipinitialspace=True).iloc[10:]
    df_u280_ddr_fast[setting] = pd.read_csv(
        f"../data/{setting}/u280-ddr-fast.csv", skipinitialspace=True).iloc[10:]

    dfs = [df_u50_slow, df_u280_slow, df_u280_ddr_slow, df_u50_fast, df_u280_fast, df_u280_ddr_fast]
    labels = ["U50 HBM 200 MHz", "U280 HBM 200 MHz", "U280 DDR 200 MHz",
              "U50 HBM unlimited", "U280 HBM unlimited", "U280 DDR unlimited"]

    # Sum up data transfer + kernel execution time,
    # time_cpu seems to be measured incorrectly for Proteus currently
    for i in range(len(dfs)):
        dfs[i][setting]["transfer+kernel"] = dfs[i][setting]["data_to_fpga_ocl"] + \
            dfs[i][setting]["kernel_ocl"] + dfs[i][setting]["data_to_host_ocl"]
        # Average standard deviation is the square root of the average variance,
        # variance is stddev ** 2
        avg_variance = (dfs[i][setting]["data_to_fpga_ocl_stddev"] ** 2 +
                        dfs[i][setting]["kernel_ocl_stddev"] ** 2 +
                        dfs[i][setting]["data_to_host_ocl_stddev"] ** 2) / 3
        dfs[i][setting]["transfer+kernel_stddev"] = np.sqrt(avg_variance)

        # Host only without transfer + kernel
        dfs[i][setting]["average_host"] = dfs[i][setting]["average"] - \
            dfs[i][setting]["transfer+kernel"]

        # Ignore cl_wide_mem_rw
        mask = dfs[i][setting]["app_name"].isin(["cl_wide_mem_rw"])
        dfs[i][setting] = dfs[i][setting][~mask].reset_index(drop=True)

# Native vs Proteus plot ------------------------------------------------------------------------------------

app_names = df_u50_slow[setting]["app_name"].values
# Remove cl_
app_names = [s[3:] for s in app_names]
# Remove _strm
for i in range(len(app_names)):
    if app_names[i] == "wide_mem_rw_strm":
        app_names[i] = "wide_mem_rw"

# use abbreviations as app names
xlabel_names = []
for app in app_names:
    xlabel_names.append(common.app_names_abb[app])

x = np.arange(len(xlabel_names))
dfs = [df_u50_fast, df_u280_fast, df_u280_ddr_fast]
labels = ["U50 native", "U50 Proteus", "U280 nat.",
          "U280 Pro.", "U280-DDR nat.", "U280-DDR Pro."]

# Total execution time --------------------------------------------------------------------------------------

upper_bar_colors = ["#5783d4", "#de8a54", "#46b097"]

x_offs = -2
for i in range(3):
    # Native
    plt.bar(x + x_offs * bar_width, dfs[i]["native"]["transfer+kernel"].values,
            hatch=hatches[0], label=labels[2 * i], color=colors[2 * i], **bar_args)
    plt.bar(x + x_offs * bar_width, dfs[i]["native"]["average_host"].values,
            bottom=dfs[i]["native"]["transfer+kernel"].values, color=upper_bar_colors[i], **bar_args)
    plt.errorbar(x + x_offs * bar_width, dfs[i]["native"]["average"].values,
                 yerr=dfs[i]["native"]["stddev"].values, **errorbar_args)
    x_offs += 1
    # Proteus
    bars_low = plt.bar(x + x_offs * bar_width, dfs[i]["proteus"]["transfer+kernel"].values,
                       hatch=hatches[1], label=labels[2 * i + 1], color=colors[2 * i], ** bar_args)
    bars_high = plt.bar(x + x_offs * bar_width, dfs[i]["proteus"]["average_host"].values,
                        bottom=dfs[i]["proteus"]["transfer+kernel"].values,
                        hatch=hatches[1], color=upper_bar_colors[i], **bar_args)
    proteus_overhead = ((dfs[i]["proteus"]["average"].values / dfs[i]
                        ["native"]["average"].values) * 100) - 100
    # for j, (bl, bh) in enumerate(zip(bars_low, bars_high)):
    #     plt.text(bl.get_x(), bl.get_height() + bh.get_height(),
    #              f"  {proteus_overhead[j]:.1f}%", rotation=90, size=8)
    plt.errorbar(x + x_offs * bar_width, dfs[i]["proteus"]["average"].values,
                 yerr=dfs[i]["proteus"]["stddev"].values, **errorbar_args)
    x_offs += 1

plt.xticks(x, xlabel_names, rotation=0)
plt.ylim(0,19.9)
plt.ylabel("Total execution time (s)")
# x_margin, y_margin = plt.margins()
# plt.margins(y=y_margin + 0.23)
plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=3, prop={'size': 8}, bbox_to_anchor=(-0.14, 1.18))
plt.tight_layout()
configure_ax()

filename = f"../plots/time-memory-total.pdf"
print(f"Saving figure to {filename}")
plt.margins(x=0.01, tight=True)
plt.savefig(filename, **savefig_args)
plt.clf()

