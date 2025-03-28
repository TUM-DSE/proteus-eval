#!/usr/bin/env python3

import common as fp
from common import (
    plt, np, pd, sns
)

plot_name = "mig-and-snapshot-oh"
data_subdir = "proteus"

# Find a CSV file for inputs
cp_data_name = "vm-state-oh"
csvfile = f"{fp.data_rootdir}/{data_subdir}/{cp_data_name}.csv"
df_cp = pd.read_csv(csvfile, sep=",")
print(df_cp)

mig_data_name = "migration-oh"
csvfile = f"{fp.data_rootdir}/{data_subdir}/{mig_data_name}.csv"
df_mig = pd.read_csv(csvfile, sep=",")
print(df_mig)

fpgas = ["u50-fast", "u280-fast", "u280-ddr-fast"]
labels = ["U50 HBM", "U280 HBM", "U280 DDR"]
colors = [[fp.bar_blue, fp.bar_orange], [fp.bar_brown, fp.bar_green], [fp.bar_grey, fp.bar_purple]]
sig_sizes = [100, 500, 1000]

# Initialize a plot
plt.rcParams.update({'font.size': 8})
width = 5
aspect = 1.6
height = width/aspect
bar_width = 0.05
x_offs = -6 * bar_width
fig, ax = plt.subplots(figsize=(width, height))

for i, (fpga, label, color) in enumerate(zip(fpgas, labels, colors)):
    # Get numbers and labels
    np_labels = df_cp.loc[df_cp["fpga"] == fpga]["signal_size[MB]"].to_numpy(dtype=str)
    np_save_fpga_cp = df_cp.loc[df_cp["fpga"] == fpga]["save_fpga[s]"].to_numpy(dtype=float)
    np_load_fpga_cp = df_cp.loc[df_cp["fpga"] == fpga]["load_fpga[s]"].to_numpy(dtype=float)
    np_save_vm_cp = df_cp.loc[df_cp["fpga"] == fpga]["save_vm[s]"].to_numpy(dtype=float)
    np_load_vm_cp = df_cp.loc[df_cp["fpga"] == fpga]["load_vm[s]"].to_numpy(dtype=float)
    np_save_fpga_mig = df_mig.loc[df_mig["fpga"] == fpga]["save_fpga[s]"].to_numpy(dtype=float)
    np_load_fpga_mig = df_mig.loc[df_mig["fpga"] == fpga]["load_fpga[s]"].to_numpy(dtype=float)
    np_save_vm_mig = df_mig.loc[df_mig["fpga"] == fpga]["save_vm[s]"].to_numpy(dtype=float)
    np_load_vm_mig = df_mig.loc[df_mig["fpga"] == fpga]["load_vm[s]"].to_numpy(dtype=float)

    # Show some numbers shown in the paper
    save_fpga_in_save_mig = np.array([np_save_fpga_mig/(np_save_fpga_mig+np_save_vm_mig)])
    load_fpga_in_load_mig = np.array([np_load_fpga_mig/(np_load_fpga_mig+np_load_vm_mig)])
    save_fpga_in_save_cp = np.array([np_save_fpga_cp/(np_save_fpga_cp+np_save_vm_cp)])
    load_fpga_in_load_cp = np.array([np_load_fpga_cp/(np_load_fpga_cp+np_load_vm_cp)])

    # Create bars
    x_pos_r1 = np.arange(len(np_labels))
    x_pos_r2 = x_pos_r1 + bar_width
    x_pos_r3 = x_pos_r2 + bar_width
    x_pos_r4 = x_pos_r3 + bar_width

    # NOTE: keep the order of the following ax.bar() to fix the order of items shown in the legend.
    ax.bar(x_pos_r1 + x_offs, np_save_fpga_mig, bar_width,
        color=fp.bar_blue,   edgecolor='k', label=f'FPGA evict' if i == 0 else '', zorder=2)
    ax.bar(x_pos_r1 + x_offs, np_save_vm_mig,   bar_width, bottom=np_save_fpga_mig,
        color=fp.bar_green,  edgecolor='k', hatch='//', label=f'VM save (mig)' if i == 0 else '', zorder=2)
    ax.bar(x_pos_r3 + x_offs, np_save_fpga_cp, bar_width,
        color=fp.bar_blue,   edgecolor='k', zorder=2)
    ax.bar(x_pos_r3 + x_offs, np_save_vm_cp,   bar_width, bottom=np_save_fpga_cp,
        color=fp.bar_purple,  edgecolor='k', hatch='//', label='Checkpoint' if i == 0 else '', zorder=2)
    ax.bar(x_pos_r2 + x_offs, np_load_fpga_mig, bar_width,
        color=fp.bar_orange, edgecolor='k', label='FPGA resume' if i == 0 else '', zorder=2)
    ax.bar(x_pos_r2 + x_offs, np_load_vm_mig,   bar_width, bottom=np_load_fpga_mig,
        color=fp.bar_brown,  edgecolor='k', hatch='..', label='VM load (mig)' if i == 0 else '', zorder=2)
    ax.bar(x_pos_r4 + x_offs, np_load_fpga_cp, bar_width,
        color=fp.bar_orange, edgecolor='k', zorder=2)
    ax.bar(x_pos_r4 + x_offs, np_load_vm_cp,   bar_width, bottom=np_load_fpga_cp,
        color=fp.bar_grey,  edgecolor='k', hatch='..', label='Restore' if i == 0 else '', zorder=2)

    x_offs += 6 * bar_width

# define x/y labels and legends
ax.set_xticks((x_pos_r1+x_pos_r2+x_pos_r3+x_pos_r4)/4, np_labels, rotation=0)
ax.set_xticklabels(np_labels, rotation=0)
ax.set_xlabel('Input/output data on FPGA [MiB]', labelpad=1.0)
ax.set_ylabel('Time [s]')
ax.legend(loc='upper left', fancybox=True, shadow=True,
          ncol=2, fontsize=6.5, bbox_to_anchor=(0, 1.0))

# define plot flames
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.grid(axis='y', zorder=1)

# save the plot as pdf
plt.tight_layout()
plt.margins(x=0.02, tight=True)
plt.savefig(f"{fp.plot_dir}/proteus/{plot_name}.pdf", dpi=300,
            pad_inches=0.02, bbox_inches='tight', format='pdf')
