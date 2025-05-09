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


df_u50_slow = {}
df_u50_fast = {}
df_u280_slow = {}
df_u280_fast = {}
df_u280_ddr_slow = {}
df_u280_ddr_fast = {}

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
width = 14.0
aspect = 4
height = width / aspect
plt.figure(figsize=(width, height))

# Individual plots ------------------------------------------------------------------------------------------

for setting in ["native", "proteus"]:

    # First 12 rows are the Vitis Accel Examples
    df_u50_slow[setting] = pd.read_csv(
        f"../data/{setting}/u50-slow.csv", skipinitialspace=True).iloc[:13]
    df_u50_fast[setting] = pd.read_csv(
        f"../data/{setting}/u50-fast.csv", skipinitialspace=True).iloc[:13]
    df_u280_slow[setting] = pd.read_csv(
        f"../data/{setting}/u280-slow.csv", skipinitialspace=True).iloc[:13]
    df_u280_fast[setting] = pd.read_csv(
        f"../data/{setting}/u280-fast.csv", skipinitialspace=True).iloc[:13]
    df_u280_ddr_slow[setting] = pd.read_csv(
        f"../data/{setting}/u280-ddr-slow.csv", skipinitialspace=True).iloc[:13]
    df_u280_ddr_fast[setting] = pd.read_csv(
        f"../data/{setting}/u280-ddr-fast.csv", skipinitialspace=True).iloc[:13]

    dfs = [df_u50_slow, df_u280_slow, df_u280_ddr_slow, df_u50_fast, df_u280_fast, df_u280_ddr_fast]
    labels = ["U50 HBM 200 MHz", "U280 HBM 200 MHz", "U280 DDR 200 MHz",
              "U50 HBM unlimited", "U280 HBM unlimited", "U280 DDR unlimited"]

    # Sum up data transfer + kernel execution time,
    # time_cpu seems to be measured incorrectly for Proteus currently
    for i in range(len(dfs)):
        dfs[i][setting]["transfer+kernel"] = dfs[i][setting]["data_to_fpga_ocl"] + \
            dfs[i][setting]["kernel_ocl"] + dfs[i][setting]["data_to_host_ocl"]
        # Average standard deviation is the square root of the average variance, variance is stddev ** 2
        avg_variance = (dfs[i][setting]["data_to_fpga_ocl_stddev"] ** 2 + dfs[i][setting]
                        ["kernel_ocl_stddev"] ** 2 + dfs[i][setting]["data_to_host_ocl_stddev"] ** 2) / 3
        dfs[i][setting]["transfer+kernel_stddev"] = np.sqrt(avg_variance)

        # Host only without transfer + kernel
        dfs[i][setting]["average_host"] = dfs[i][setting]["average"] - \
            dfs[i][setting]["transfer+kernel"]

        # Ignore cl_wide_mem_rw
        mask = dfs[i][setting]["app_name"].isin(["cl_wide_mem_rw"])
        dfs[i][setting] = dfs[i][setting][~mask].reset_index(drop=True)

        avg_all_apps = dfs[i][setting].loc[:, "average"].mean()
        avg_tk_all_apps = dfs[i][setting].loc[:, "transfer+kernel"].mean()
        avg_host = (dfs[i][setting].loc[:, "average"] - dfs[i][setting].loc[:, "transfer+kernel"]).mean()
        new_idx = len(dfs[i][setting])
        dfs[i][setting].loc[new_idx] = {""
            "app_name": "cl_average",
            "average": avg_all_apps,
            "stddev": 0.0, # TODO: average of stddev?
            "transfer+kernel": avg_tk_all_apps,
            "average_host": avg_host}

    # app_names = df_u50_slow[setting]["app_name"].values
    # # Remove cl_
    # app_names = [s[3:] for s in app_names]

    # # use abbreviations as app names
    # xlabel_names = []
    # for app in app_names:
    #     xlabel_names.append(common.app_names_abb[app])

    # x = np.arange(len(xlabel_names))

    # # Total execution time ----------------------------------------------------------------------------------

    # for i in range(6):
    #     x_offs = i - 2
    #     plt.bar(x + x_offs * bar_width, dfs[i][setting]["average"].values,
    #             hatch=hatches[i % 2], label=labels[i], **bar_args)
    #     plt.errorbar(x + x_offs * bar_width, dfs[i][setting]["average"].values,
    #                  yerr=dfs[i][setting]["stddev"].values, **errorbar_args)

    # plt.xticks(x, xlabel_names, rotation=10)
    # plt.ylabel("Total execution time (s)")
    # plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=3, bbox_to_anchor=(0, 1.0))
    # plt.tight_layout()
    # configure_ax()

    # filename = f"../plots/{setting}/time-xilinx-total.pdf"
    # print(f"Saving figure to {filename}")
    # plt.margins(x=0.01, tight=True)
    # plt.savefig(filename, **savefig_args)
    # plt.clf()

    # # Data transfer + kernel time ---------------------------------------------------------------------------

    # for i in range(6):
    #     x_offs = i - 2
    #     plt.bar(x + x_offs * bar_width, dfs[i][setting]["transfer+kernel"].values,
    #             hatch=hatches[i % 2], label=labels[i], **bar_args)
    #     plt.errorbar(x + x_offs * bar_width, dfs[i][setting]["transfer+kernel"].values,
    #                  yerr=dfs[i][setting]["transfer+kernel_stddev"].values, **errorbar_args)

    # plt.xticks(x, xlabel_names, rotation=10)
    # plt.ylabel("Total data transfer + kernel time (s)")
    # plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=3, bbox_to_anchor=(0, 1.0))
    # plt.tight_layout()
    # configure_ax()

    # filename = f"../plots/{setting}/time-xilinx-fpga.pdf"
    # print(f"Saving figure to {filename}")
    # plt.margins(x=0.01, tight=True)
    # plt.savefig(filename, **savefig_args)
    # plt.clf()

# Native vs Proteus plot ------------------------------------------------------------------------------------

bar_width = 0.12
app_names = df_u50_slow[setting]["app_name"].values
# Remove cl_
app_names = [s[3:] for s in app_names]
# Remove _strm
for i in range(len(app_names)):
    if app_names[i] == "wide_mem_rw_strm":
        app_names[i] = "wide_mem_rw"

xlabel_names = []
for app in app_names:
    xlabel_names.append(common.app_names_abb[app])

x = np.arange(len(xlabel_names))
dfs = [df_u50_fast, df_u280_fast, df_u280_ddr_fast]
labels = ["U50 native", "U50 Proteus", "U280 native",
          "U280 Proteus", "U280-DDR native", "U280-DDR Proteus"]

# Total execution time --------------------------------------------------------------------------------------

upper_bar_colors = ["#5783d4", "#de8a54", "#46b097"]

x_offs = -2.5
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
                       hatch=hatches[1], label=labels[2 * i + 1], color=colors[2 * i], **bar_args)
    bars_high = plt.bar(x + x_offs * bar_width, dfs[i]["proteus"]["average_host"].values,
                        bottom=dfs[i]["proteus"]["transfer+kernel"].values,
                        hatch=hatches[1], color=upper_bar_colors[i], **bar_args)
    proteus_overhead = ((dfs[i]["proteus"]["average"].values /
                        dfs[i]["native"]["average"].values) * 100) - 100
    for j, (bl, bh) in enumerate(zip(bars_low, bars_high)):
        plt.text(bl.get_x() + 0.01, bl.get_height() + bh.get_height(),
                 f"  {proteus_overhead[j]:.1f}%", rotation=90, size=9)
    plt.errorbar(x + x_offs * bar_width, dfs[i]["proteus"]["average"].values,
                 yerr=dfs[i]["proteus"]["stddev"].values, **errorbar_args)
    x_offs += 1

plt.xticks(x, xlabel_names, rotation=0)
plt.ylabel("Total execution time (s)")
plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=3, prop={'size': 10}, bbox_to_anchor=(0, 1.0))
plt.tight_layout()
configure_ax()

filename = f"../plots/time-xilinx-total.pdf"
print(f"Saving figure to {filename}")
plt.margins(x=0.005, tight=True)
plt.savefig(filename, **savefig_args)
plt.clf()

# Data transfer + kernel time -------------------------------------------------------------------------------

x_offs = -2
for i in range(3):
    # Native
    plt.bar(x + x_offs * bar_width, dfs[i]["native"]["transfer+kernel"].values,
            hatch=hatches[0], label=labels[2 * i], **bar_args)
    plt.errorbar(x + x_offs * bar_width, dfs[i]["native"]["transfer+kernel"].values,
                 yerr=dfs[i]["native"]["transfer+kernel_stddev"].values, **errorbar_args)
    x_offs += 1
    # Proteus
    bars = plt.bar(x + x_offs * bar_width, dfs[i]["proteus"]["transfer+kernel"].values,
                   hatch=hatches[1], label=labels[2 * i + 1], **bar_args)
    proteus_overhead = ((dfs[i]["proteus"]["transfer+kernel"].values /
                         dfs[i]["native"]["transfer+kernel"].values) * 100) - 100
    for j, b in enumerate(bars):
        plt.text(b.get_x() + 0.19 * bar_width, b.get_height() + 1.5,
                 f"{proteus_overhead[j]:.1f}%", rotation=90, size=8)
    plt.errorbar(x + x_offs * bar_width, dfs[i]["proteus"]["transfer+kernel"].values,
                 yerr=dfs[i]["proteus"]["transfer+kernel_stddev"].values, **errorbar_args)
    x_offs += 1

plt.xticks(x, xlabel_names, rotation=10)
plt.ylabel("Total data transfer + kernel time (s)")
plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=3, bbox_to_anchor=(0, 1.0))
plt.tight_layout()
configure_ax()

filename = f"../plots/time-xilinx-fpga.pdf"
print(f"Saving figure to {filename}")
plt.margins(x=0.01, tight=True)
plt.savefig(filename, **savefig_args)
plt.clf()
