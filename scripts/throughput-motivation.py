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

bar_width = 0.14

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

gib = 1024 * 1024 * 1024

df_u50_slow = pd.read_csv(f"../data/native/u50-300mhz.csv", skipinitialspace=True)
df_u50_fast = pd.read_csv(f"../data/native/u50-400mhz.csv", skipinitialspace=True)
df_u280_slow = pd.read_csv(f"../data/native/u280-300mhz.csv", skipinitialspace=True)
df_u280_fast = pd.read_csv(f"../data/native/u280-400mhz.csv", skipinitialspace=True)
df_u280_ddr_slow = pd.read_csv(f"../data/native/u280-ddr-300mhz.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv(f"../data/native/u280-ddr-400mhz.csv", skipinitialspace=True)

dfs = [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]
labels = ["U50 lo", "U50 hi", "U280 lo",
          "U280 hi", "U280-DDR lo", "U280-DDR hi"]
# labels = ["U50 loclk", "U50 hiclk", "U280 loclk",
#           "U280 hiclk", "U280-DDR loclk", "U280-DDR hiclk"]

# Sum up data transfer + kernel execution time,
# time_cpu seems to be measured incorrectly for Proteus currently.
for i in range(len(dfs)):
    dfs[i]["transfer+kernel"] = dfs[i]["data_to_fpga_ocl"] + \
        dfs[i]["kernel_ocl"] + dfs[i]["data_to_host_ocl"]
    # Average standard deviation is the square root of the average variance, variance is stddev ** 2
    avg_variance = (dfs[i]["data_to_fpga_ocl_stddev"] ** 2 + dfs[i]
                    ["kernel_ocl_stddev"] ** 2 + dfs[i]["data_to_host_ocl_stddev"] ** 2) / 3
    dfs[i]["transfer+kernel_stddev"] = np.sqrt(avg_variance)

    in_size = dfs[i]["kernel_input_data_size"] * dfs[i]["kernel_iterations"]
    out_size = dfs[i]["kernel_output_data_size"] * dfs[i]["kernel_iterations"]
    # Throughput in GB/s
    dfs[i]["thrp_to_fpga"] = in_size / dfs[i]["data_to_fpga_ocl"] / gib
    dfs[i]["thrp_kernel"] = (in_size + out_size) / dfs[i]["kernel_ocl"] / gib
    dfs[i]["thrp_to_host"] = out_size / dfs[i]["data_to_host_ocl"] / gib
    dfs[i]["thrp"] = (in_size + out_size) / dfs[i]["transfer+kernel"] / gib

### Split data into compute-bound and memory-bound apps
dfs_comp = []
dfs_mem = []
for df in dfs:
    df_comp = df[:2]
    dfs_comp.append(df_comp)
    df_mem = df[2:]
    dfs_mem.append(df_mem)

comp_app_names = dfs_comp[0]["app_name"].values
mem_app_names = dfs_mem[0]["app_name"].values

# Remove cl_
comp_app_names = [s[3:] for s in comp_app_names]
mem_app_names = [s[3:] for s in mem_app_names]

# Remove _strm, change hello_world name
for i in range(len(comp_app_names)):
    if comp_app_names[i] == "helloworld":
        comp_app_names[i] = "vector_add"

for i in range(len(mem_app_names)):
    if mem_app_names[i] == "wide_mem_rw_strm":
        mem_app_names[i] = "wide_mem_rw"

# use abbreviations as app names
cmp_xlabel_names = []
mem_xlabel_names = []
for app in comp_app_names:
    cmp_xlabel_names.append(common.app_names_abb[app])
for app in mem_app_names:
    mem_xlabel_names.append(common.app_names_abb[app])

### Preparation to create plots
width = 4.2
height = 1.6
# aspect = 2
# height = width / aspect
width_comp = width * (2.2/5)
width_mem = width * (2.8/5)

colors = [common.bar_blue, common.bar_blue, common.bar_orange,
          common.bar_orange, common.bar_green, common.bar_green]
hatches = ["", "//"]

### For compute-bound apps
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
plt.rcParams.update({'font.size': 8})
plt.figure(figsize=(width_comp, height))

x = np.arange(len(cmp_xlabel_names))
for i in range(len(dfs_comp)):
    x_offs = i - 2
    plt.bar(x + x_offs * bar_width, dfs_comp[i]["thrp_kernel"].values,
            hatch=hatches[i % 2], label=labels[i], **bar_args)

plt.ylim(0,1.7)
plt.xticks(x, cmp_xlabel_names, rotation=0)
plt.margins(x=0.01, tight=True)
plt.ylabel("Kernel thrp. (GiB/s)")
# plt.legend(loc='upper left', fancybox=True, shadow=True,
#            fontsize=8, ncol=1, bbox_to_anchor=(0, 0.98))
plt.tight_layout()
configure_ax()

filename_comp = f"../plots/native/throughput-motivation-comp.pdf"
print(f"Saving figure to {filename_comp}")
plt.savefig(filename_comp, **savefig_args)
plt.show()
plt.clf()

### For memory-bound apps
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
plt.rcParams.update({'font.size': 7.5})
plt.figure(figsize=(width_mem, height))

x2 = np.arange(len(mem_xlabel_names))
for i in range(len(dfs_mem)):
    x2_offs = i - 2
    plt.bar(x2 + x2_offs * bar_width, dfs_mem[i]["thrp_kernel"].values,
            hatch=hatches[i % 2], label=labels[i], **bar_args)

plt.xticks(x2, mem_xlabel_names, rotation=0)
plt.ylim(0,70)
plt.yticks(np.arange(0, 60, 10))
plt.ylabel("Kernel thrp. (GiB/s)", fontsize=7)
plt.legend(loc='upper left', fancybox=True, shadow=True, # fontsize=7, 
           ncol=2, prop={'size': 6.2}, bbox_to_anchor=(-0.03, 1.18))
plt.tight_layout()
configure_ax()

filename_mem = f"../plots/native/throughput-motivation-mem.pdf"
print(f"Saving figure to {filename_mem}")
plt.margins(x=0.01, tight=True)
plt.savefig(filename_mem, **savefig_args)
plt.clf()
