#!/usr/bin/env python3

import common as fp
from common import (
    plt, np, pd, sns
)


# Find a CSV file for inputs
data_subdir = "proteus"
data_name = "fpga-state-oh"
csvfile = f"{fp.data_rootdir}/{data_subdir}/{data_name}.csv"
df = pd.read_csv(csvfile, sep=",")

fpgas = ["u50-fast", "u280-fast", "u280-ddr-fast"]
labels = ["U50 HBM", "U280 HBM", "U280 DDR"]
colors = [[fp.bar_blue, fp.bar_blue], [fp.bar_orange, fp.bar_orange], [fp.bar_green, fp.bar_green]]
hatches = ["", "//"]
sig_sizes = [100, 500, 1000]

# Initialize a plot
plt.rcParams.update({'font.size': 8})
width = 5
aspect = 2
height = width/aspect
bar_width = 0.1
x_offs = -2 * bar_width
fig, ax = plt.subplots(figsize=(width, height))

for fpga, label, color in zip(fpgas, labels, colors):
    # Get numbers and labels
    np_save_fpga = df.loc[df["fpga"] == fpga]["save_fpga[s]"].to_numpy(dtype=float)
    np_load_fpga = df.loc[df["fpga"] == fpga]["load_fpga[s]"].to_numpy(dtype=float)
    np_work_init = df.loc[df["fpga"] == fpga]["worker_init[s]"].to_numpy(dtype=float)
    np_labels = df.loc[df["fpga"] == fpga]["signal_size[MB]"].to_numpy(dtype=str)

    savefpga_stddev_index = df.columns.get_loc("save_fpga[s]")+1
    np_savefpga_stddev = df.loc[df["fpga"] == fpga].iloc[:,
                                                         savefpga_stddev_index].to_numpy(dtype=float)
    loadfpga_stddev_index = df.columns.get_loc("load_fpga[s]")+1
    np_loadfpga_stddev = df.loc[df["fpga"] == fpga].iloc[:,
                                                         loadfpga_stddev_index].to_numpy(dtype=float)

    # Create bars
    x_positions = np.arange(len(np_labels))
    ax.bar(x_positions + x_offs - bar_width/2, np_save_fpga, bar_width, hatch=hatches[0], yerr=np_savefpga_stddev,
           error_kw={'elinewidth': 1, 'capsize': 2},  color=color[0], edgecolor='k', label=f"{label} evict", zorder=2)
    ax.bar(x_positions + x_offs + bar_width/2, np_load_fpga, bar_width, hatch=hatches[1], yerr=np_loadfpga_stddev,
           error_kw={'elinewidth': 1, 'capsize': 2}, color=color[1], edgecolor='k', label=f"{label} resume", zorder=2)

    x_offs += 2 * bar_width

# define x/y labels and legends
ax.set_xticks(x_positions)
ax.set_xticklabels(np_labels, rotation=0)
ax.set_xlabel('Input/output data on FPGA [MiB]', labelpad=1.0)
ax.set_ylabel('Time [s]')
ax.legend(loc='upper left', fancybox=True, shadow=True,
          ncol=2, prop={'size': 7}, bbox_to_anchor=(0, 1))

# define plot flames
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.grid(axis='y', zorder=1)

# save the plot as pdf
plt.tight_layout()
plt.margins(x=0.02, tight=True)
plt.savefig(f"{fp.plot_dir}/proteus/{data_name}.pdf", dpi=300,
            pad_inches=0.02, bbox_inches='tight', format='pdf')
