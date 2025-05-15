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

bar_width = 0.18

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

# mem_app_names = ["wide_mem_rw", "wide_mem_rw_2x", "wide_mem_rw_4x",
#                  "gmem_2banks", "gmem_2banks_2x", "gmem_2banks_4x"]

mem_app_patterns = ["wide_mem_rw", "gmem_2banks"]

ros_app_names = ["3d-rendering", "digit-recognition", "optical-flow", "spam-filter"]

# Get app dfs
dfs = []
dfs_mem = []
cmp_app_names = []
mem_app_names = []
for app in app_names:
    df_app = pd.read_csv(f"../sched_sim/{app}.csv", skipinitialspace=True)
    dfs.append(df_app.copy())
    if any(mem_app in app for mem_app in mem_app_patterns):
        mem_app_names.append(app)
    else:
        cmp_app_names.append(app)
        # dfs_mem.append(df_app.copy())
        # print(f"{app} detected")

# print(dfs)
# print(dfs_mem)
# exit(0)

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
worst_cmp_rows = []
worst_mem_rows = []
worst_ros_rows = []
for i, df_app in enumerate(dfs):
    idx = df_app["thrp"].idxmin()
    worst_rows.append(df_app.iloc[[idx]])

    # For separate plots
    if any(app_names[i] == mem_app for mem_app in mem_app_names):
        worst_mem_rows.append(df_app.iloc[[idx]])
    elif any(app_names[i] == ros_app for ros_app in ros_app_names):
        worst_ros_rows.append(df_app.iloc[[idx]])
    else:
        worst_cmp_rows.append(df_app.iloc[[idx]])

df_worst = pd.concat(worst_rows, ignore_index=True)
# print(df_worst)

# dfs for separate plots
df_worst_cmp = pd.concat(worst_cmp_rows, ignore_index=True)
df_worst_mem = pd.concat(worst_mem_rows, ignore_index=True)
df_worst_ros = pd.concat(worst_ros_rows, ignore_index=True)
print(df_worst_cmp)
print(df_worst_mem)
print(df_worst_ros)

# Best case
best_rows = []
best_cmp_rows = []
best_mem_rows = []
best_ros_rows = []
print("----------Best-----------")
for i, df_app in enumerate(dfs):
    idx = df_app["thrp"].idxmax()
    best_rows.append(df_app.iloc[[idx]])

    # For separate plots
    if any(app_names[i] == mem_app for mem_app in mem_app_names):
        best_mem_rows.append(df_app.iloc[[idx]])
    elif any(app_names[i] == ros_app for ros_app in ros_app_names):
        best_ros_rows.append(df_app.iloc[[idx]])
    else:
        best_cmp_rows.append(df_app.iloc[[idx]])

df_best = pd.concat(best_rows, ignore_index=True)
# print(df_best)

# dfs for separate plots
df_best_cmp = pd.concat(best_cmp_rows, ignore_index=True)
df_best_mem = pd.concat(best_mem_rows, ignore_index=True)
df_best_ros = pd.concat(best_ros_rows, ignore_index=True)
print(df_best_cmp)
print(df_best_mem)
print(df_best_ros)

# Proteus (freq-only)
print("----------Freq-----------")
freq_rows = []
freq_cmp_rows = []
freq_mem_rows = []
freq_ros_rows = []
for i, df_app in enumerate(dfs):
    # choose the FPGA(s) with the highest (best) score
    best_score = df_score_freq[app_names[i]].max()
    df_best_scores = df_score_freq[df_score_freq[app_names[i]] == best_score]
    indices = df_best_scores.index.tolist()

    # choose the worst case if multiple FPGAs
    df_best_fpgas = df_app.iloc[indices]
    idx = df_best_fpgas['thrp'].idxmax()
    freq_rows.append(df_app.iloc[[idx]])

    # For separate plots
    if any(app_names[i] == mem_app for mem_app in mem_app_names):
        freq_mem_rows.append(df_app.iloc[[idx]])
    elif any(app_names[i] == ros_app for ros_app in ros_app_names):
        freq_ros_rows.append(df_app.iloc[[idx]])
    else:
        freq_cmp_rows.append(df_app.iloc[[idx]])

df_freq = pd.concat(freq_rows, ignore_index=True)
# print(df_freq)

# dfs for separate plots
df_freq_cmp = pd.concat(freq_cmp_rows, ignore_index=True)
df_freq_mem = pd.concat(freq_mem_rows, ignore_index=True)
df_freq_ros = pd.concat(freq_ros_rows, ignore_index=True)
print(df_freq_cmp)
print(df_freq_mem)
print(df_freq_ros)

# Proteus
print("---------Proteus---------")
proteus_rows = []
proteus_cmp_rows = []
proteus_mem_rows = []
proteus_ros_rows = []
for i, df_app in enumerate(dfs):
    # choose the FPGA(s) with the highest (best) score
    best_score = df_score_new[app_names[i]].min()
    df_best_scores = df_score_new[df_score_new[app_names[i]] == best_score]
    indices = df_best_scores.index.tolist()

    # choose the worst case if multiple FPGAs
    df_best_fpgas = df_app.iloc[indices]
    idx = df_best_fpgas['thrp'].idxmin()
    proteus_rows.append(df_app.iloc[[idx]])

    # For separate plots
    if any(app_names[i] == mem_app for mem_app in mem_app_names):
        proteus_mem_rows.append(df_app.iloc[[idx]])
    elif any(app_names[i] == ros_app for ros_app in ros_app_names):
        proteus_ros_rows.append(df_app.iloc[[idx]])
    else:
        proteus_cmp_rows.append(df_app.iloc[[idx]])

df_proteus = pd.concat(proteus_rows, ignore_index=True)
# print(df_proteus)

# dfs for separate plots
df_proteus_cmp = pd.concat(proteus_cmp_rows, ignore_index=True)
df_proteus_mem = pd.concat(proteus_mem_rows, ignore_index=True)
df_proteus_ros = pd.concat(proteus_ros_rows, ignore_index=True)
print(df_proteus_cmp)
print(df_proteus_mem)
print(df_proteus_ros)

dfs_plot = [df_worst, df_best, df_freq, df_proteus]
dfs_plot_mem = [df_worst_mem, df_best_mem, df_freq_mem, df_proteus_mem]
dfs_plot_cmp = [df_worst_cmp, df_best_cmp, df_freq_cmp, df_proteus_cmp]
dfs_plot_ros = [df_worst_ros, df_best_ros, df_freq_ros, df_proteus_ros]
labels = ["Worst", "Best", "Proteus (Fmax)", "Proteus"]
# labels = ["Best", "Worst", "Proteus"]
          # "Freq-only(2nd)", "Proteus", "Proteus(2nd)"]

### Calculate the average performance gain compared to the worst case
best_improve    = 100.0 * (df_best['thrp']    - df_worst['thrp']) / df_worst['thrp']
freq_improve    = 100.0 * (df_freq['thrp']    - df_worst['thrp']) / df_worst['thrp']
proteus_improve = 100.0 * (df_proteus['thrp'] - df_worst['thrp']) / df_worst['thrp']

best_improve_cmp    = 100.0 * (df_best_cmp['thrp']    - df_worst_cmp['thrp']) / df_worst_cmp['thrp']
freq_improve_cmp    = 100.0 * (df_freq_cmp['thrp']    - df_worst_cmp['thrp']) / df_worst_cmp['thrp']
proteus_improve_cmp = 100.0 * (df_proteus_cmp['thrp'] - df_worst_cmp['thrp']) / df_worst_cmp['thrp']

best_improve_mem    = 100.0 * (df_best_mem['thrp']    - df_worst_mem['thrp']) / df_worst_mem['thrp']
freq_improve_mem    = 100.0 * (df_freq_mem['thrp']    - df_worst_mem['thrp']) / df_worst_mem['thrp']
proteus_improve_mem = 100.0 * (df_proteus_mem['thrp'] - df_worst_mem['thrp']) / df_worst_mem['thrp']

best_improve_ros    = 100.0 * (df_best_ros['thrp']    - df_worst_ros['thrp']) / df_worst_ros['thrp']
freq_improve_ros    = 100.0 * (df_freq_ros['thrp']    - df_worst_ros['thrp']) / df_worst_ros['thrp']
proteus_improve_ros = 100.0 * (df_proteus_ros['thrp'] - df_worst_ros['thrp']) / df_worst_ros['thrp']

improves = [best_improve, freq_improve, proteus_improve]
improves_cmp = [best_improve_cmp, freq_improve_cmp, proteus_improve_cmp]
improves_mem = [best_improve_mem, freq_improve_mem, proteus_improve_mem]
improves_ros = [best_improve_ros, freq_improve_ros, proteus_improve_ros]

print(f"Best          : {best_improve.mean()}")
print(f"Proteus (freq): {freq_improve.mean()}")
print(f"Proteus       : {proteus_improve.mean()}")

### Preparation to create plots
# width = 15.0
# aspect = 4.2
width = 14.0
height = 3.5
# aspect = 4.0
# height = width / aspect
width_cmp = width * (8.8/18)
width_mem = width * (4.6/18)
width_ros = width * (4.6/18)


colors = [common.bar_blue, common.bar_orange, common.bar_green, common.bar_green]
hatches = ["", "", "", "//"]

xlabel_names = []
xlabel_names_mem = []
xlabel_names_cmp = []
xlabel_names_ros = []
mem_app_num = 0
for app in app_names:
    xlabel_names.append(common.app_names_abb[app])
    # For separate plots
    if any(app == mem_app for mem_app in mem_app_names):
        xlabel_names_mem.append(common.app_names_abb[app])
    elif any(app == ros_app for ros_app in ros_app_names):
        xlabel_names_ros.append(common.app_names_abb[app])
    else:
        xlabel_names_cmp.append(common.app_names_abb[app])

# Total throughput --------------------------------------------------------------------------------------
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
plt.rcParams.update({'font.size': 12})
plt.figure(figsize=(width, height))

# x = np.arange(len(app_names)-mem_app_num)
x = np.arange(len(xlabel_names))
for i in range(len(dfs_plot)):
    x_offs = i - 1.5
    print(f"position: {x}, {x+x_offs*bar_width}")
    bars = plt.bar(x + x_offs * bar_width, dfs_plot[i]["thrp"].values,
            hatch=hatches[i], label=labels[i], **bar_args)

    # skip the worst case (no numbers)
    if i == 0:
        continue

    for j, b in enumerate(bars):
        plt.text(b.get_x() + 0.19 * bar_width, b.get_height(),
                 f"  {improves[i-1][j]:.1f}%", rotation=90, size=8.5)

plt.xticks(x, xlabel_names, rotation=12)
plt.ylabel("Throughput (GiB/s)")
plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=4, bbox_to_anchor=(0.0, 1.1))
plt.tight_layout()
configure_ax()

filename = f"../plots/scheduler-thrp.pdf"
print(f"Saving figure to {filename}")
plt.margins(x=0.01, tight=True)
plt.savefig(filename, **savefig_args)
plt.clf()

# Total throughput (compute)  --------------------------------------------------------------------------------------
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
plt.rcParams.update({'font.size': 12})
plt.figure(figsize=(width_cmp, height))

x2 = np.arange(len(xlabel_names_cmp))
for i in range(len(dfs_plot_cmp)):
    x_offs = i - 1.5
    print(f"position: {x2}, {x2+x_offs*bar_width}")
    bars = plt.bar(x2 + x_offs * bar_width, dfs_plot_cmp[i]["thrp"].values,
            hatch=hatches[i], label=labels[i], **bar_args)

    # skip the worst case (no numbers)
    if i == 0:
        continue

    for j, b in enumerate(bars):
        plt.text(b.get_x() + 0.19 * bar_width, b.get_height(),
                 f"  {improves_cmp[i-1][j]:.1f}%", rotation=90, size=8.5)

plt.xticks(x2, xlabel_names_cmp, rotation=12)
plt.ylim(0,2.6)
plt.ylabel("Throughput (GiB/s)")
plt.legend(loc='upper right', fancybox=True, shadow=True, ncol=2, prop={'size': 11}, bbox_to_anchor=(1.0, 1.09))
plt.tight_layout()
configure_ax()

filename_cmp = f"../plots/scheduler-thrp-cmp.pdf"
print(f"Saving figure to {filename_cmp}")
plt.margins(x=0.01, tight=True)
plt.savefig(filename_cmp, **savefig_args)
plt.clf()

# Total throughput (memory)  --------------------------------------------------------------------------------------
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
plt.rcParams.update({'font.size': 12})
plt.figure(figsize=(width_mem, height))

x3 = np.arange(len(xlabel_names_mem))
for i in range(len(dfs_plot_mem)):
    x_offs = i - 1.5
    print(f"position: {x3}, {x3+x_offs*bar_width}")
    bars = plt.bar(x3 + x_offs * bar_width, dfs_plot_mem[i]["thrp"].values,
            hatch=hatches[i], label=labels[i], **bar_args)

    # skip the worst case (no numbers)
    if i == 0:
        continue

    for j, b in enumerate(bars):
        plt.text(b.get_x() + 0.19 * bar_width, b.get_height(),
                 f"  {improves_mem[i-1][j]:.1f}%", rotation=90, size=8.5)

plt.xticks(x3, xlabel_names_mem, rotation=12)
plt.ylim(0,8.0)
plt.ylabel("Throughput (GiB/s)")
# plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=4, bbox_to_anchor=(0.0, 1.1))
plt.tight_layout()
configure_ax()

filename_mem = f"../plots/scheduler-thrp-mem.pdf"
print(f"Saving figure to {filename_mem}")
plt.margins(x=0.01, tight=True)
plt.savefig(filename_mem, **savefig_args)
plt.clf()

# Total throughput (Rosetta)  --------------------------------------------------------------------------------------
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
plt.rcParams.update({'font.size': 12})
# plt.figure(figsize=(width_ros, height))
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(width_ros, height))

ax1.set_ylim(0.2, 3.0)
ax2.set_ylim(0.002, 0.12)
ax3.set_ylim(0.0, 0.0012)

# Hide the spines between plots
ax1.spines.bottom.set_visible(False)
ax2.spines.top.set_visible(False)
ax2.spines.bottom.set_visible(False)
ax3.spines.top.set_visible(False)

# Hide the top spine
ax1.spines.top.set_visible(False)

# Hide the x axis from the upper plots
ax1.get_xaxis().set_visible(False)
ax2.get_xaxis().set_visible(False)

ax1.set_axisbelow(True)
ax1.yaxis.grid()
ax2.set_axisbelow(True)
ax2.yaxis.grid()
ax3.set_axisbelow(True)
ax3.yaxis.grid()

d = .5  # Proportion of vertical to horizontal extent of the slanted line
kwargs = dict(marker=[(-1, -d), (1, d)], markersize=10,
              linestyle="none", color='k', mec='k', mew=2, clip_on=False)
ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)
ax2.plot([0, 1], [0, 0], transform=ax2.transAxes, **kwargs)
ax3.plot([0, 1], [1, 1], transform=ax3.transAxes, **kwargs)

# ax1_pos = ax1.get_position()
# ax1_pos.y0 += 0.5
# ax1.set_position(ax1_pos)

x3 = np.arange(len(xlabel_names_ros))

# Upper figure
for i in range(len(dfs_plot_ros)):
    x_offs = i - 1.5
    print(f"position: {x3}, {x3+x_offs*bar_width}")
    bars = ax1.bar(x3 + x_offs * bar_width, dfs_plot_ros[i]["thrp"].values,
            hatch=hatches[i], label=labels[i], **bar_args)

    # skip the worst case (no numbers)
    if i == 0:
        continue

    # text for other bars is shown in the lower figures
    for j in [2, 3]:
        b = bars[j]
        ax1.text(b.get_x() - 0.002, b.get_height(),
            f"  {improves_ros[i-1][j]:.1f}%", rotation=90, size=8.5)

# Middle figure
for i in range(len(dfs_plot_ros)):
    x_offs = i - 1.5
    print(f"position: {x3}, {x3+x_offs*bar_width}")
    bars = ax2.bar(x3 + x_offs * bar_width, dfs_plot_ros[i]["thrp"].values,
            hatch=hatches[i], label=labels[i], **bar_args)

    # skip the worst case (no numbers)
    if i == 0:
        continue

    j = 0
    b = bars[j]
    ax2.text(b.get_x() - 0.002, b.get_height(),
        f"  {improves_ros[i-1][j]:.1f}%", rotation=90, size=8.5)

# Lower figure
for i in range(len(dfs_plot_ros)):
    x_offs = i - 1.5
    print(f"position: {x3}, {x3+x_offs*bar_width}")
    bars = ax3.bar(x3 + x_offs * bar_width, dfs_plot_ros[i]["thrp"].values,
            hatch=hatches[i], label=labels[i], **bar_args)

    # skip the worst case (no numbers)
    if i == 0:
        continue

    j = 1
    b = bars[j]
    ax3.text(b.get_x() - 0.002, b.get_height(),
        f"  {improves_ros[i-1][j]:.1f}%", rotation=90, size=8.5)

plt.xticks(x3, xlabel_names_ros, rotation=12)
# plt.ylim(0,8.0)
ax2.set_ylabel("Throughput (GiB/s)")
ax2.yaxis.set_label_coords(-0.22, 1.1)
# plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=4, bbox_to_anchor=(0.0, 1.1))
plt.tight_layout()

filename_ros = f"../plots/scheduler-thrp-ros.pdf"
print(f"Saving figure to {filename_ros}")
plt.subplots_adjust(wspace=0, hspace=0.05)
plt.margins(x=0.01, tight=True)
plt.savefig(filename_ros, **savefig_args)
plt.clf()

