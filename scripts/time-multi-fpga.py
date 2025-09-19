#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
import common
# Python does not like filenames with dashes :(
# import importlib
# est_intel = importlib.import_module("estimate-intel-performance")

# Make sure Intel csv file is up-to-date
# est_intel.estimate_intel_performance()
# print("Intel estimation done")
# print("------------------------------------------------------------------------\n")

# df_s10_native = pd.read_csv(f"{common.data_rootdir}/native/s10-fast-estimated.csv")
# df_s10_proteus = pd.read_csv(f"{common.data_rootdir}/proteus/s10-fast-estimated.csv")
# dfs = [df_s10_native, df_s10_proteus]

# numbers are in milliseconds (?)
u50_only_ms  = [664608, 298791, 0]
u280_only_ms = [644823, 288449, 0]
proteus_ms   = [644823, 288449, 115046] # When FPGAs = 1 or 2, Proteus will choose a faster FPGA

u50_only_sec  = [x / 1000.0 for x in u50_only_ms]
u280_only_sec = [x / 1000.0 for x in u280_only_ms]
proteus_sec   = [x / 1000.0 for x in proteus_ms]

colors = [common.bar_blue, common.bar_orange, common.bar_green]
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)

plt.rcParams.update({'font.size': 10})
bar_width = 0.20
width = 4.6
height = 1.5
# aspect = 2.0
# height = width / aspect
plt.figure(figsize=(width, height))

# app_names = df_s10_proteus["app_name"].values
# # Remove cl_
# app_names = [s[3:] for s in app_names]
# # Remove _strm, change hello_world name
# for i in range(len(app_names)):
#     if app_names[i] == "wide_mem_rw_strm":
#         app_names[i] = "wide_mem_rw"
#     elif app_names[i] == "helloworld":
#         app_names[i] = "vector_add"

# # use abbreviations as app names
# xlabel_names = []
# for app in app_names:
#     xlabel_names.append(common.app_names_abb[app])

# xlabel_names = [1, 2, 4]
xlabel_names = ["1 FPGA", "2 FPGAs", "4 FPGAs"]

x = np.arange(len(xlabel_names))

bars_u50  = plt.bar(x - 1.0 * bar_width, u50_only_sec,
        bar_width, label="U50-only", linewidth=1, edgecolor="k")
bars_u280 = plt.bar(x, u280_only_sec,
               bar_width, label="U280-only", linewidth=1, edgecolor="k", hatch="//")
bars_pro  = plt.bar(x + 1.0 * bar_width, proteus_sec,
               bar_width, label="Proteus", linewidth=1, edgecolor="k", hatch="**")

# proteus_overhead = ((df_s10_proteus["average"].values /
#                     df_s10_native["average"].values) * 100) - 100
# for j, b in enumerate(bars):
#     plt.text(b.get_x()+0.07, b.get_height()+0.4,
#              f" {proteus_overhead[j]:.1f}%", rotation=90, size=8) #, fontweight='bold')

for j, b in enumerate(bars_u50):
    if u50_only_sec[j]==0:
        plt.text(b.get_x()+0.06, b.get_height()+1.5, f"X", color='red', rotation=0, size=10, fontweight='bold')

for j, b in enumerate(bars_u280):
    if u280_only_sec[j]==0:
        plt.text(b.get_x()+0.06, b.get_height()+1.5, f"X", color='red', rotation=0, size=10, fontweight='bold')

proteus_baseline = proteus_sec[0] # FPGA = 1
for j, b in enumerate(bars_pro):
    # if j != 0:
    plt.text(b.get_x()+0.0, b.get_height()+5.0, f"{(proteus_baseline / proteus_sec[j]):.1f}x", 
             rotation=0, size=9, fontweight='bold')


plt.xticks(x, xlabel_names, rotation=0)
# plt.xlabel("Number of FPGAs")
plt.yticks(np.arange(0, 301, 100))
plt.ylabel("Total time (s)")
x_margin, y_margin = plt.margins()
# plt.margins(y=y_margin + 0.1)
plt.legend(loc='upper right', fancybox=True, shadow=True, ncol=1, prop={'size': 8}, bbox_to_anchor=(1.0, 1.0))
plt.tight_layout()

ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
# ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis='y')

filename = f"{common.plot_dir}/time-multi-fpga.pdf"
print(f"Saving figure to {filename}")
plt.margins(x=0.06, tight=True)
plt.savefig(filename, dpi=300, pad_inches=0.02, bbox_inches="tight", format="pdf")
# plt.show()
