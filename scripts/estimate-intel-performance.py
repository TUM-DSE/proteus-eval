#!/usr/bin/env python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
import common


def estimate_intel_performance():
    print("a")


data_subdir = "proteus"

df_s10 = pd.read_csv(f"{common.data_rootdir}/{data_subdir}/s10-fast-measured.csv")
print(df_s10)
df_u280_ddr_fast = pd.read_csv(f"{common.data_rootdir}/{data_subdir}/u280-ddr-fast.csv")
print(df_u280_ddr_fast)
df_freq = pd.read_csv(f"{common.data_rootdir}/frequencies.csv")

app_names = df_s10["app_name"].values

mask = df_u280_ddr_fast["app_name"].isin(app_names)
df_u280_ddr_fast = df_u280_ddr_fast[mask].reset_index(drop=True)
print(df_u280_ddr_fast)

mask = df_freq["app_name"].isin(app_names)
df_freq = df_freq[mask].reset_index(drop=True)
print(df_freq)

df_s10_est = pd.DataFrame()
df_s10_est["app_name"] = app_names

# Time without fpga = average - data_to_fpga_ocl - kernel_ocl - data_to_host_ocl

average_without_fpga = df_s10["average"] - df_s10["data_to_fpga_ocl"] - \
    df_s10["kernel_ocl"] - df_s10["data_to_host_ocl"]
print("Average without FPGA:")
print(average_without_fpga)

# Use U280 values for data transfer time estimation
est_data_to_fpga = df_u280_ddr_fast["data_to_fpga_ocl"]
print("to fpga")
print(est_data_to_fpga)
est_data_to_host = df_u280_ddr_fast["data_to_host_ocl"]
print("to host")
print(est_data_to_host)

# s10_kernel_time = u280_kernel_time * (u280_freq / s10_freq)
freq_ratios = df_freq["u280_ddr_fast_freq"] / df_freq["s10_fast_freq"]
print("freq ratios")
print(freq_ratios)
est_kernel = df_u280_ddr_fast["kernel_ocl"] * freq_ratios
print("est kernel")
print(est_kernel)
print("U280 kernel")
print(df_u280_ddr_fast["kernel_ocl"])

df_s10_est["average"] = 0.0
df_s10_est["stddev"] = 0.0
df_s10_est["kernel_input_data_size"] = df_s10["kernel_input_data_size"]
df_s10_est["kernel_output_data_size"] = df_s10["kernel_output_data_size"]
df_s10_est["kernel_iterations"] = df_s10["kernel_iterations"]
df_s10_est["time_cpu"] = 0.0
df_s10_est["time_cpu_stddev"] = 0.0
df_s10_est["data_to_fpga_ocl"] = est_data_to_fpga
df_s10_est["data_to_fpga_ocl_stddev"] = 0.0
df_s10_est["kernel_ocl"] = est_kernel
df_s10_est["kernel_ocl_stddev"] = 0.0
df_s10_est["data_to_host_ocl"] = est_data_to_host
df_s10_est["data_to_host_ocl_stddev"] = 0.0

print(df_s10_est)

est_filename = f"{common.data_rootdir}/{data_subdir}/s10-fast-estimated.csv"
print(f"Saving performance estimation to {est_filename}")
df_s10_est.to_csv(est_filename, index=False)
