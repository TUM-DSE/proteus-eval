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

bar_width = 0.16

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

# Get scores
df_score_freq = pd.read_csv(f"../sched_sim/scores_freq.csv", skipinitialspace=True)
df_score_new  = pd.read_csv(f"../sched_sim/scores_new.csv", skipinitialspace=True)
dfs_score = [df_score_freq, df_score_new]

app_names = [item for item in df_score_new.columns]
del app_names[0]
print(app_names)

# Get app dfs
dfs = []
for app in app_names:
    df_app = pd.read_csv(f"../sched_sim/{app}.csv", skipinitialspace=True)
    dfs.append(df_app.copy())
# print(dfs)

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

### Create dfs for each scoring algorithm
# Worst case
print("----------Worst----------")
worst_rows = []
for i, df_app in enumerate(dfs):
    idx = df_app["thrp"].idxmin()
    worst_rows.append(df_app.iloc[[idx]])
    # print(f"{app_names[i]}: {idx}")
    # print(f"{df_app.iloc[idx]['thrp']}")

df_worst = pd.concat(worst_rows, ignore_index=True)
print(df_worst)

# Best case
best_rows = []
print("----------Best-----------")
for i, df_app in enumerate(dfs):
    idx = df_app["thrp"].idxmax()
    best_rows.append(df_app.iloc[[idx]])

df_best = pd.concat(best_rows, ignore_index=True)
print(df_best)
    
# Proteus (freq-only)
print("----------Freq-----------")
freq_rows = []
for i, df_app in enumerate(dfs):
    # choose the FPGA(s) with the highest (best) score
    best_score = df_score_freq[app_names[i]].max()
    df_best_scores = df_score_freq[df_score_freq[app_names[i]] == best_score]
    indices = df_best_scores.index.tolist()

    # choose the worst case if multiple FPGAs
    df_best_fpgas = df_app.iloc[indices]
    idx = df_best_fpgas['thrp'].idxmax()
    freq_rows.append(df_app.iloc[[idx]])

df_freq = pd.concat(freq_rows, ignore_index=True)
print(df_freq)

# Proteus 
print("---------Proteus---------")
proteus_rows = []
for i, df_app in enumerate(dfs):
    # choose the FPGA(s) with the highest (best) score
    best_score = df_score_new[app_names[i]].min()
    df_best_scores = df_score_new[df_score_new[app_names[i]] == best_score]
    indices = df_best_scores.index.tolist()

    # choose the worst case if multiple FPGAs
    df_best_fpgas = df_app.iloc[indices]
    idx = df_best_fpgas['thrp'].idxmin()
    proteus_rows.append(df_app.iloc[[idx]])

df_proteus = pd.concat(proteus_rows, ignore_index=True)
print(df_proteus)

dfs_plot = [df_worst, df_best, df_freq, df_proteus]
labels = ["Worst", "Best", "Proteus (fmax-only)", "Proteus"]
# labels = ["Best", "Worst", "Proteus"]
          # "Freq-only(2nd)", "Proteus", "Proteus(2nd)"]

### Calculate the average performance gain compared to the worst case
best_improve = 100.0 * (df_best['thrp'] - df_worst['thrp']) / df_worst['thrp']
freq_improve = 100.0 * (df_freq['thrp'] - df_worst['thrp']) / df_worst['thrp']
proteus_improve = 100.0 * (df_proteus['thrp'] - df_worst['thrp']) / df_worst['thrp']

improves = [best_improve, freq_improve, proteus_improve]

print(f"Best          : {best_improve.mean()}")
print(f"Proteus (freq): {freq_improve.mean()}")
print(f"Proteus       : {proteus_improve.mean()}")

### Preparation to create plots
width = 15.0
aspect = 4.2
height = width / aspect

colors = [common.bar_blue, common.bar_orange, common.bar_green, common.bar_green]
hatches = ["", "", "", "//"]

plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
plt.rcParams.update({'font.size': 12})
plt.figure(figsize=(width, height))
# plt.yscale("log")


# Total throughput --------------------------------------------------------------------------------------
x = np.arange(len(app_names))
for i in range(len(dfs_plot)):
    x_offs = i - 2
    bars = plt.bar(x + x_offs * bar_width, dfs_plot[i]["thrp"].values,
            hatch=hatches[i], label=labels[i], **bar_args)

    if i == 0:
        continue

    for j, b in enumerate(bars):
        plt.text(b.get_x() + 0.19 * bar_width, b.get_height(),
                 f"  {improves[i-1][j]:.1f}%", rotation=90, size=8)

plt.xticks(x, app_names, rotation=18)
plt.ylabel("Throughput (GiB/s)")
plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=4, bbox_to_anchor=(0, 1.16))
plt.tight_layout()
configure_ax()

filename = f"../plots/scheduler-thrp.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, **savefig_args)
plt.clf()

