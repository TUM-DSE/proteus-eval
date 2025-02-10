#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

for setting in ["native", "proteus"]:

    # First 10 rows compute intensive applications, remaining rows memory intensive applications
    df_u50_slow = pd.read_csv(f"../data/{setting}/u50-slow.csv", skipinitialspace=True).iloc[:10]
    df_u50_fast = pd.read_csv(f"../data/{setting}/u50-fast.csv", skipinitialspace=True).iloc[:10]
    df_u280_slow = pd.read_csv(f"../data/{setting}/u280-slow.csv", skipinitialspace=True).iloc[:10]
    df_u280_fast = pd.read_csv(f"../data/{setting}/u280-fast.csv", skipinitialspace=True).iloc[:10]
    df_u280_ddr_slow = pd.read_csv(f"../data/{setting}/u280-ddr-slow.csv", skipinitialspace=True).iloc[:10]
    df_u280_ddr_fast = pd.read_csv(f"../data/{setting}/u280-ddr-fast.csv", skipinitialspace=True).iloc[:10]

    # Sum up data transfer + kernel execution time
    for df in [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]:
        df["transfer+kernel"] = df["data_to_fpga_ocl"] + df["kernel_ocl"] + df["data_to_host_ocl"]

    bar_width = 0.12
    app_names = df_u50_slow["app_name"].values
    x = np.arange(len(app_names))

    # Total execution time --------------------------------------------------------------------------------------

    plt.bar(x - 2 * bar_width, df_u50_slow["average"].values, width=bar_width, label=f"U50 HBM 200 MHz")
    plt.bar(x - 1 * bar_width, df_u280_slow["average"].values, width=bar_width, label=f"U280 HBM 200 MHz")
    plt.bar(x                , df_u280_ddr_slow["average"].values, width=bar_width, label=f"U280 DDR 200 MHz")
    plt.bar(x + 1 * bar_width, df_u50_fast["average"].values, width=bar_width, label="U50 HBM unlimited")
    plt.bar(x + 2 * bar_width, df_u280_fast["average"].values, width=bar_width, label="U280 HBM unlimited")
    plt.bar(x + 3 * bar_width, df_u280_ddr_fast["average"].values, width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x, app_names, rotation=30, ha="right")
    plt.ylabel("Total execution time (s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/time-compute-total.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

    # Data transfer + kernel time -------------------------------------------------------------------------------

    plt.bar(x - 2 * bar_width, df_u50_slow["transfer+kernel"].values, width=bar_width, label=f"U50 HBM 200 MHz")
    plt.bar(x - 1 * bar_width, df_u280_slow["transfer+kernel"].values, width=bar_width, label=f"U280 HBM 200 MHz")
    plt.bar(x                , df_u280_ddr_slow["transfer+kernel"].values, width=bar_width, label=f"U280 DDR 200 MHz")
    plt.bar(x + 1 * bar_width, df_u50_fast["transfer+kernel"].values, width=bar_width, label="U50 HBM unlimited")
    plt.bar(x + 2 * bar_width, df_u280_fast["transfer+kernel"].values, width=bar_width, label="U280 HBM unlimited")
    plt.bar(x + 3 * bar_width, df_u280_ddr_fast["transfer+kernel"].values, width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x, app_names, rotation=30, ha="right")
    plt.ylabel("Data transfer + kernel time (s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/time-compute-fpga.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
