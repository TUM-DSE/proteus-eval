#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import statistics as stat
import common
# Python does not like filenames with dashes :(
import importlib
est_intel = importlib.import_module("estimate-intel-performance")


matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# Make sure Intel csv file is up-to-date
est_intel.estimate_intel_performance()
print("Intel estimation done")
print("------------------------------------------------------------------------\n")

df_s10_native = pd.read_csv(f"{common.data_rootdir}/native/s10-fast-estimated.csv")
df_s10_proteus = pd.read_csv(f"{common.data_rootdir}/proteus/s10-fast-estimated.csv")
dfs = [df_s10_native, df_s10_proteus]

colors = [common.bar_blue, common.bar_orange]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

plt.rcParams.update({'font.size': 10})
bar_width = 0.28
width = 4.0
height = 2.0
# aspect = 2.0
# height = width / aspect
plt.figure(figsize=(width, height))

app_names = df_s10_proteus["app_name"].values
# Remove cl_
app_names = [s[3:] for s in app_names]
# Remove _strm, change hello_world name
for i in range(len(app_names)):
    if app_names[i] == "wide_mem_rw_strm":
        app_names[i] = "wide_mem_rw"
    elif app_names[i] == "helloworld":
        app_names[i] = "vector_add"

# use abbreviations as app names
xlabel_names = []
for app in app_names:
    xlabel_names.append(common.app_names_abb[app])

x = np.arange(len(xlabel_names))

plt.bar(x - 0.5 * bar_width, df_s10_native["average"].values,
        bar_width, label="S10-emu native", linewidth=1, edgecolor="k")
bars = plt.bar(x + 0.5 * bar_width, df_s10_proteus["average"].values,
               bar_width, label="S10-emu Proteus", linewidth=1, edgecolor="k", hatch="//")

proteus_overhead = ((df_s10_proteus["average"].values /
                    df_s10_native["average"].values) * 100) - 100
for j, b in enumerate(bars):
    plt.text(b.get_x()+0.07, b.get_height()+0.8,
             f"{proteus_overhead[j]:.1f}%", rotation=90, size=8) #, fontweight='bold')

plt.xticks(x, xlabel_names, rotation=0)
plt.ylabel("Total execution time (s)")
x_margin, y_margin = plt.margins()
# plt.margins(y=y_margin + 0.1)
plt.legend(loc='upper left', fancybox=True, shadow=True, ncol=1, prop={'size': 8}, bbox_to_anchor=(0, 1.18))
plt.tight_layout()

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis='y')

filename = f"{common.plot_dir}/time-intel.pdf"
print(f"Saving figure to {filename}")
plt.margins(x=0.03, tight=True)
plt.savefig(filename, dpi=300, pad_inches=0.02, bbox_inches="tight", format="pdf")
# plt.show()
