#!/usr/bin/env python3

import common as fp
from common import (
    plt, np, pd, sns
)


def add_line(ax, xpos, ypos):
    line = plt.Line2D([xpos, xpos], [ypos+0.194, ypos-0.05], transform=ax.transAxes, color='black', linewidth=0.7)
    line.set_clip_on(False)
    ax.add_line(line)


plot_name = "mig-and-snapshot-oh"
data_subdir = "proteus"

# Find a CSV file for inputs
cp_data_name = "vm-state-oh"
csvfile = f"{fp.data_rootdir}/{data_subdir}/{cp_data_name}.csv"
df_cp = pd.read_csv(csvfile, sep=",")

mig_data_name = "migration-oh"
csvfile = f"{fp.data_rootdir}/{data_subdir}/{mig_data_name}.csv"
df_mig = pd.read_csv(csvfile, sep=",")

fpgas = ["u50-fast", "u280-fast", "u280-ddr-fast"]
labels = [
    "U50",
    "U280",
    # "U280-\nDDR",
    "DDR",
    "U50",
    "U280",
    # "U280-\nDDR",
    "DDR",
    "U50",
    "U280",
    # "U280-\nDDR",
    "DDR",
]

# Initialize a plot
plt.rcParams.update({'font.size': 10})
bar_width = 0.19
width = 4.0
height = 2.8
fig, ax = plt.subplots(figsize=(width, height))

np_save_fpga_cp = df_cp["save_fpga[s]"].to_numpy(dtype=float)
np_load_fpga_cp = df_cp["load_fpga[s]"].to_numpy(dtype=float)
np_save_vm_cp = df_cp["save_vm[s]"].to_numpy(dtype=float)
np_load_vm_cp = df_cp["load_vm[s]"].to_numpy(dtype=float)
np_save_fpga_mig = df_mig["save_fpga[s]"].to_numpy(dtype=float)
np_load_fpga_mig = df_mig["load_fpga[s]"].to_numpy(dtype=float)
np_save_vm_mig = df_mig["save_vm[s]"].to_numpy(dtype=float)
np_load_vm_mig = df_mig["load_vm[s]"].to_numpy(dtype=float)

# Show some numbers shown in the paper
# save_fpga_in_save_mig = np.array([np_save_fpga_mig/(np_save_fpga_mig+np_save_vm_mig)])
# load_fpga_in_load_mig = np.array([np_load_fpga_mig/(np_load_fpga_mig+np_load_vm_mig)])
# save_fpga_in_save_cp = np.array([np_save_fpga_cp/(np_save_fpga_cp+np_save_vm_cp)])
# load_fpga_in_load_cp = np.array([np_load_fpga_cp/(np_load_fpga_cp+np_load_vm_cp)])

# print(save_fpga_in_save_mig)
# print(load_fpga_in_load_mig)
# print(save_fpga_in_save_cp )
# print(load_fpga_in_load_cp )

# Create bars
x_pos_r1 = np.arange(len(labels))
x_pos_r2 = x_pos_r1 + bar_width
x_pos_r3 = x_pos_r2 + bar_width
x_pos_r4 = x_pos_r3 + bar_width

print("% of FPGA evict in eviction:")
print(np_save_fpga_mig / (np_save_fpga_mig + np_save_vm_mig) * 100)
print(np_save_fpga_cp / (np_save_fpga_cp + np_save_vm_cp) * 100)
print("% of FPGA resume in resuming:")
print(np_load_fpga_mig / (np_load_fpga_mig + np_load_vm_mig) * 100)
print(np_load_fpga_cp / (np_load_fpga_cp + np_load_vm_cp) * 100)

# NOTE: keep the order of the following ax.bar() to fix the order of items shown in the legend.
ax.bar(x_pos_r1, np_save_fpga_mig, bar_width, color=fp.bar_blue,
       edgecolor='k', label='FPGA evict', zorder=2)
ax.bar(x_pos_r2, np_load_fpga_mig, bar_width, color=fp.bar_orange,
       edgecolor='k', label='FPGA resume', zorder=2)
ax.bar(x_pos_r1, np_save_vm_mig,   bar_width, bottom=np_save_fpga_mig,
       color=fp.bar_green,  edgecolor='k', hatch='//', label='VM save-mig', zorder=2)
ax.bar(x_pos_r2, np_load_vm_mig,   bar_width, bottom=np_load_fpga_mig,
       color=fp.bar_brown,  edgecolor='k', hatch='..', label='VM load-mig', zorder=2)
ax.bar(x_pos_r3, np_save_fpga_cp, bar_width, color=fp.bar_blue,   edgecolor='k', zorder=2)
ax.bar(x_pos_r3, np_save_vm_cp,   bar_width, bottom=np_save_fpga_cp,
       color=fp.bar_purple,  edgecolor='k', hatch='//', label='Checkpoint', zorder=2)
ax.bar(x_pos_r4, np_load_fpga_cp, bar_width, color=fp.bar_orange, edgecolor='k', zorder=2)
ax.bar(x_pos_r4, np_load_vm_cp,   bar_width, bottom=np_load_fpga_cp,
       color=fp.bar_grey,  edgecolor='k', hatch='..', label='Restore', zorder=2)

# define x/y labels and legends
ax.set_xticks((x_pos_r1+x_pos_r2+x_pos_r3+x_pos_r4)/4, labels)
ax.set_xticklabels(labels, rotation=0, fontsize=8.5)
plt.ylim(0,9)
ax.set_ylabel('Time (s)')
# x_margin, y_margin = plt.margins()
# plt.margins(y=y_margin + 0.3)
ax.legend(loc='upper left', fancybox=True, shadow=True, # fontsize=6.5,
          ncol=3, prop={'size': 8}, bbox_to_anchor=(-0.13, 1.05))

# define plot flames
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.grid(axis='y', zorder=1)

add_line(ax, 0, -.2)
add_line(ax, 0.333, -.2)
add_line(ax, 0.666, -.2)
add_line(ax, 1, -.2)

plt.text(0.5, -1.8,  "Src: U50",       fontsize=9.5)
plt.text(3.35, -1.8,  "Src: U280",       fontsize=9.5)
plt.text(5.9, -1.8, "Src: U280-DDR",    fontsize=9.5)

# save the plot as pdf
plt.tight_layout()
plt.margins(x=0.02, tight=True)
plt.savefig(f"{fp.plot_dir}/proteus/{plot_name}.pdf", dpi=300,
            pad_inches=0.02, bbox_inches='tight', format='pdf')
