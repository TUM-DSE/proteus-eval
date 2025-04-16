#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


for setting in ["native", "proteus"]:

    df_u50_slow = pd.read_csv(f"../data/{setting}/u50-slow.csv", skipinitialspace=True)
    df_u50_fast = pd.read_csv(f"../data/{setting}/u50-fast.csv", skipinitialspace=True)
    df_u280_slow = pd.read_csv(f"../data/{setting}/u280-slow.csv", skipinitialspace=True)
    df_u280_fast = pd.read_csv(f"../data/{setting}/u280-fast.csv", skipinitialspace=True)
    df_u280_ddr_slow = pd.read_csv(f"../data/{setting}/u280-ddr-slow.csv", skipinitialspace=True)
    df_u280_ddr_fast = pd.read_csv(f"../data/{setting}/u280-ddr-fast.csv", skipinitialspace=True)
    dfs = [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]

    for df in dfs:
        in_size = df["kernel_input_data_size"] * df["kernel_iterations"]
        out_size = df["kernel_output_data_size"] * df["kernel_iterations"]
        # Throughput in MB/s
        df["thrp_to_fpga"] = in_size / df["data_to_fpga_ocl"] / 1_000_000
        df["thrp_kernel"] = in_size / df["kernel_ocl"] / 1_000_000
        df["thrp_to_host"] = out_size / df["data_to_host_ocl"] / 1_000_000

    bar_width = 0.12
    app_names = df_u50_slow["app_name"].values
    x = np.arange(len(app_names))

    # Throughput host to FPGA ---------------------------------------------------------------------------------------------

    plt.bar(x - 2 * bar_width, df_u50_slow["thrp_to_fpga"].values,
            width=bar_width, label=f"U50 HBM limited")
    plt.bar(x - 1 * bar_width, df_u280_slow["thrp_to_fpga"].values,
            width=bar_width, label=f"U280 HBM limited")
    plt.bar(x, df_u280_ddr_slow["thrp_to_fpga"].values, width=bar_width, label=f"U280 DDR limited")
    plt.bar(x + 1 * bar_width, df_u50_fast["thrp_to_fpga"].values,
            width=bar_width, label="U50 HBM unlimited")
    plt.bar(x + 2 * bar_width, df_u280_fast["thrp_to_fpga"].values,
            width=bar_width, label="U280 HBM unlimited")
    plt.bar(x + 3 * bar_width,
            df_u280_ddr_fast["thrp_to_fpga"].values, width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x, app_names, rotation=40, ha="right")
    plt.ylabel("Throughput Host to FPGA (MB/s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/throughput-to-fpga.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

    # Throughput kernel compute intensive apps ----------------------------------------------------------------------------

    plt.bar(x[:10] - 2 * bar_width, df_u50_slow["thrp_kernel"].iloc[:10].values,
            width=bar_width, label=f"U50 HBM 200 MHz")
    plt.bar(x[:10] - 1 * bar_width, df_u280_slow["thrp_kernel"].iloc[:10].values,
            width=bar_width, label=f"U280 HBM 200 MHz")
    plt.bar(x[:10], df_u280_ddr_slow["thrp_kernel"].iloc[:10].values,
            width=bar_width, label=f"U280 DDR 200 MHz")
    plt.bar(x[:10] + 1 * bar_width, df_u50_fast["thrp_kernel"].iloc[:10].values,
            width=bar_width, label="U50 HBM unlimited")
    plt.bar(x[:10] + 2 * bar_width, df_u280_fast["thrp_kernel"].iloc[:10].values,
            width=bar_width, label="U280 HBM unlimited")
    plt.bar(x[:10] + 3 * bar_width, df_u280_ddr_fast["thrp_kernel"].iloc[:10].values,
            width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x[:10], app_names[:10], rotation=30, ha="right")
    plt.ylabel("Throughput FPGA kernel (MB/s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/throughput-kernel-compute.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

    # Throughput kernel memory intensive apps -----------------------------------------------------------------------------

    plt.bar(x[10:] - 2 * bar_width, df_u50_slow["thrp_kernel"].iloc[10:].values,
            width=bar_width, label=f"U50 HBM 300 MHz")
    plt.bar(x[10:] - 1 * bar_width, df_u280_slow["thrp_kernel"].iloc[10:].values,
            width=bar_width, label=f"U280 HBM 300 MHz")
    plt.bar(x[10:], df_u280_ddr_slow["thrp_kernel"].iloc[10:].values,
            width=bar_width, label=f"U280 DDR 300 MHz")
    plt.bar(x[10:] + 1 * bar_width, df_u50_fast["thrp_kernel"].iloc[10:].values,
            width=bar_width, label="U50 HBM unlimited")
    plt.bar(x[10:] + 2 * bar_width, df_u280_fast["thrp_kernel"].iloc[10:].values,
            width=bar_width, label="U280 HBM unlimited")
    plt.bar(x[10:] + 3 * bar_width, df_u280_ddr_fast["thrp_kernel"].iloc[10:].values,
            width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x[10:], app_names[10:], rotation=30, ha="right")
    plt.ylabel("Throughput FPGA kernel (MB/s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/throughput-kernel-memory.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()

    # Throughput FPGA to host ---------------------------------------------------------------------------------------------

    plt.bar(x - 2 * bar_width, df_u50_slow["thrp_to_host"].values,
            width=bar_width, label=f"U50 HBM limited")
    plt.bar(x - 1 * bar_width, df_u280_slow["thrp_to_host"].values,
            width=bar_width, label=f"U280 HBM limited")
    plt.bar(x, df_u280_ddr_slow["thrp_to_host"].values, width=bar_width, label=f"U280 DDR limited")
    plt.bar(x + 1 * bar_width, df_u50_fast["thrp_to_host"].values,
            width=bar_width, label="U50 HBM unlimited")
    plt.bar(x + 2 * bar_width, df_u280_fast["thrp_to_host"].values,
            width=bar_width, label="U280 HBM unlimited")
    plt.bar(x + 3 * bar_width,
            df_u280_ddr_fast["thrp_to_host"].values, width=bar_width, label="U280 DDR unlimited")

    plt.xticks(x, app_names, rotation=40, ha="right")
    plt.ylabel("Throughput FPGA to host (MB/s)")
    plt.legend()
    plt.tight_layout()

    filename = f"../plots/{setting}/throughput-to-host.pdf"
    print(f"Saving figure to {filename}")
    plt.savefig(filename, format="pdf")
    plt.clf()
