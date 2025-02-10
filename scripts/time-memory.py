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

    plt.bar(x - 2 * bar_width, df_u50_slow[setting]["time_cpu"].values, width=bar_width, label=f"U50 HBM 300 MHz")
    plt.bar(x - 1 * bar_width, df_u280_slow[setting]["time_cpu"].values, width=bar_width, label=f"U280 HBM 300 MHz")
    plt.bar(x                , df_u280_ddr_slow[setting]["time_cpu"].values, width=bar_width, label=f"U280 DDR 300 MHz")
    plt.bar(x + 1 * bar_width, df_u50_fast[setting]["time_cpu"].values, width=bar_width, label="U50 HBM unlimited")
    plt.bar(x + 2 * bar_width, df_u280_fast[setting]["time_cpu"].values, width=bar_width, label="U280 HBM unlimited")
    plt.bar(x + 3 * bar_width, df_u280_ddr_fast[setting]["time_cpu"].values, width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x, app_names, rotation=20)
    plt.ylabel("Data transfer + kernel time (s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/time-memory-fpga.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

# Native vs Proteus plot ---------------------------------------------------------------------------------------------

bar_width = 0.3
app_names = df_u50_slow[setting]["app_name"].values
x = np.arange(len(app_names))

# Total execution time --------------------------------------------------------------------------------------

avg_native = df_u50_slow["native"]["average"]
avg_proteus = df_u50_fast["proteus"]["average"]

for df in [df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]:
    avg_native += df["native"]["average"]
    avg_proteus += df["proteus"]["average"]

avg_native /= 6
avg_proteus /= 6

plt.bar(x, avg_native.values, width=bar_width, label="Native")
plt.bar(x + bar_width, avg_proteus.values, width=bar_width, label="Proteus")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average total execution time (s)")
plt.legend()
plt.tight_layout()

filename = f"../plots/time-memory-total.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
plt.clf()

# Data transfer + kernel time -------------------------------------------------------------------------------

avg_native = df_u50_slow["native"]["time_cpu"]
avg_proteus = df_u50_fast["proteus"]["time_cpu"]

for df in [df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]:
    avg_native += df["native"]["time_cpu"]
    avg_proteus += df["proteus"]["time_cpu"]

avg_native /= 6
avg_proteus /= 6

plt.bar(x, avg_native.values, width=bar_width, label="Native")
plt.bar(x + bar_width, avg_proteus.values, width=bar_width, label="Proteus")

plt.xticks(x, app_names, rotation=30, ha="right")
plt.ylabel("Average data transfer + kernel time (s)")
plt.legend()
plt.tight_layout()

filename = f"../plots/time-memory-fpga.pdf"
print(f"Saving figure to {filename}")
plt.savefig(filename, format="pdf")
plt.clf()
