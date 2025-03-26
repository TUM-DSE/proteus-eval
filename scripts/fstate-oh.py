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
print(df)

# Get numbers and labels
np_save_fpga = df["save_fpga[s]"].to_numpy(dtype=float)
np_load_fpga = df["load_fpga[s]"].to_numpy(dtype=float)
np_work_init = df["worker_init[s]"].to_numpy(dtype=float)
np_labels = df["signal_size[MB]"].to_numpy(dtype=str)

savefpga_stddev_index = df.columns.get_loc("save_fpga[s]")+1
np_savefpga_stddev = df.iloc[:, savefpga_stddev_index].to_numpy(dtype=float)
loadfpga_stddev_index = df.columns.get_loc("load_fpga[s]")+1
np_loadfpga_stddev = df.iloc[:, loadfpga_stddev_index].to_numpy(dtype=float)

# Initialize a plot
plt.rcParams.update({'font.size': 8})
width = 3.3
aspect = 1.6
height = width/aspect
fig, ax = plt.subplots(figsize=(width, height))

# Create bars
x_positions = np.arange(len(np_labels))
bar_width = 0.4
ax.bar(x_positions - bar_width/2, np_save_fpga, bar_width, yerr=np_savefpga_stddev,
       error_kw={'elinewidth': 1, 'capsize': 2},  color=fp.bar_blue, edgecolor='k', label='FPGA evict', zorder=2)
ax.bar(x_positions + bar_width/2, np_work_init, bar_width, bottom=np_load_fpga-np_work_init, yerr=np_loadfpga_stddev,
       error_kw={'elinewidth': 1, 'capsize': 2}, color=fp.bar_orange, edgecolor='k', hatch='//', label='Worker init', zorder=3)
ax.bar(x_positions + bar_width/2, np_load_fpga, bar_width,
       color=fp.bar_orange, edgecolor='k', label='FPGA resume', zorder=2)

# define x/y labels and legends
ax.set_xticks(x_positions)
ax.set_xticklabels(np_labels, rotation=0)
ax.set_xlabel('Input/output data on FPGA [MiB]', labelpad=1.0)
ax.set_ylabel('Time [s]')
ax.legend(loc='upper left', fancybox=True, shadow=True,
          ncol=2, prop={'size': 7}, bbox_to_anchor=(0, 1.12))

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
