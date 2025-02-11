#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_u50_slow = {}
df_u50_fast = {}
df_u280_slow = {}
df_u280_fast = {}
df_u280_ddr_slow = {}
df_u280_ddr_fast = {}

for setting in ["native", "proteus"]:

    # First 10 rows compute intensive applications, remaining rows memory intensive applications
    df_u50_slow[setting] = pd.read_csv(f"../data/{setting}/u50-slow.csv", skipinitialspace=True).iloc[10:]
    df_u50_fast[setting] = pd.read_csv(f"../data/{setting}/u50-fast.csv", skipinitialspace=True).iloc[10:]
    df_u280_slow[setting] = pd.read_csv(f"../data/{setting}/u280-slow.csv", skipinitialspace=True).iloc[10:]
    df_u280_fast[setting] = pd.read_csv(f"../data/{setting}/u280-fast.csv", skipinitialspace=True).iloc[10:]
    df_u280_ddr_slow[setting] = pd.read_csv(f"../data/{setting}/u280-ddr-slow.csv", skipinitialspace=True).iloc[10:]
    df_u280_ddr_fast[setting] = pd.read_csv(f"../data/{setting}/u280-ddr-fast.csv", skipinitialspace=True).iloc[10:]

    # Sum up data transfer + kernel execution time, time_cpu seems to be measured incorrectly for Proteus currently
    for df in [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]:
        df[setting]["transfer+kernel"] = df[setting]["data_to_fpga_ocl"] + df[setting]["kernel_ocl"] + df[setting]["data_to_host_ocl"]

    bar_width = 0.12
    app_names = df_u50_slow[setting]["app_name"].values
    x = np.arange(len(app_names))

    # Total execution time --------------------------------------------------------------------------------------

    plt.bar(x - 2 * bar_width, df_u50_slow[setting]["average"].values, width=bar_width, label=f"U50 HBM 300 MHz")
    plt.bar(x - 1 * bar_width, df_u280_slow[setting]["average"].values, width=bar_width, label=f"U280 HBM 300 MHz")
    plt.bar(x                , df_u280_ddr_slow[setting]["average"].values, width=bar_width, label=f"U280 DDR 300 MHz")
    plt.bar(x + 1 * bar_width, df_u50_fast[setting]["average"].values, width=bar_width, label="U50 HBM unlimited")
    plt.bar(x + 2 * bar_width, df_u280_fast[setting]["average"].values, width=bar_width, label="U280 HBM unlimited")
    plt.bar(x + 3 * bar_width, df_u280_ddr_fast[setting]["average"].values, width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x, app_names, rotation=20)
    plt.ylabel("Total execution time (s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/time-memory-total.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

    # Data transfer + kernel time -------------------------------------------------------------------------------

    plt.bar(x - 2 * bar_width, df_u50_slow[setting]["transfer+kernel"].values, width=bar_width, label=f"U50 HBM 300 MHz")
    plt.bar(x - 1 * bar_width, df_u280_slow[setting]["transfer+kernel"].values, width=bar_width, label=f"U280 HBM 300 MHz")
    plt.bar(x                , df_u280_ddr_slow[setting]["transfer+kernel"].values, width=bar_width, label=f"U280 DDR 300 MHz")
    plt.bar(x + 1 * bar_width, df_u50_fast[setting]["transfer+kernel"].values, width=bar_width, label="U50 HBM unlimited")
    plt.bar(x + 2 * bar_width, df_u280_fast[setting]["transfer+kernel"].values, width=bar_width, label="U280 HBM unlimited")
    plt.bar(x + 3 * bar_width, df_u280_ddr_fast[setting]["transfer+kernel"].values, width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x, app_names, rotation=20)
    plt.ylabel("Data transfer + kernel time (s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/time-memory-fpga.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

# Native vs Proteus plot ---------------------------------------------------------------------------------------------

bar_width = 0.12
app_names = df_u50_slow[setting]["app_name"].values
x = np.arange(len(app_names))

# Total execution time --------------------------------------------------------------------------------------

plt.bar(x - 2 * bar_width, df_u50_fast["native"]["average"].values, width=bar_width, label="U50 HBM native")
plt.bar(x - 1 * bar_width, df_u50_fast["proteus"]["average"].values, width=bar_width, label="U50 HBM Proteus")
plt.bar(x                , df_u280_fast["native"]["average"].values, width=bar_width, label="U280 HBM native")
plt.bar(x + 1 * bar_width, df_u280_fast["proteus"]["average"].values, width=bar_width, label="U280 HBM Proteus")
plt.bar(x + 2 * bar_width, df_u280_ddr_fast["native"]["average"].values, width=bar_width, label="U280 DDR native")
plt.bar(x + 3 * bar_width, df_u280_ddr_fast["proteus"]["average"].values, width=bar_width, label="U280 DDR Proteus")


plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average total execution time (s)")
plt.ylim(top=30)
plt.legend()
plt.tight_layout()

filename = f"../plots/time-memory-total.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
plt.clf()

# Data transfer + kernel time -------------------------------------------------------------------------------

plt.bar(x - 2 * bar_width, df_u50_fast["native"]["transfer+kernel"].values, width=bar_width, label="U50 HBM native")
plt.bar(x - 1 * bar_width, df_u50_fast["proteus"]["transfer+kernel"].values, width=bar_width, label="U50 HBM Proteus")
plt.bar(x                , df_u280_fast["native"]["transfer+kernel"].values, width=bar_width, label="U280 HBM native")
plt.bar(x + 1 * bar_width, df_u280_fast["proteus"]["transfer+kernel"].values, width=bar_width, label="U280 HBM Proteus")
plt.bar(x + 2 * bar_width, df_u280_ddr_fast["native"]["transfer+kernel"].values, width=bar_width, label="U280 DDR native")
plt.bar(x + 3 * bar_width, df_u280_ddr_fast["proteus"]["transfer+kernel"].values, width=bar_width, label="U280 DDR Proteus")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average data transfer + kernel time (s)")
plt.ylim(top=15)
plt.legend()
plt.tight_layout()

filename = f"../plots/time-memory-fpga.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
plt.clf()
