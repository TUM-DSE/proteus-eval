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
df_u280_ddr_fast = df_u280_ddr_fast[mask]
print(df_u280_ddr_fast)

mask = df_freq["app_name"].isin(app_names)
df_freq = df_freq[mask]
print(df_freq)

df_s10_est = pd.DataFrame()
df_s10_est["app_name"] = app_names

# Time without fpga = average - data_to_fpga_ocl - kernel_ocl - data_to_host_ocl

df_s10_est["average"] = 0.0
df_s10_est["stddev"] = 0.0
df_s10_est["kernel_input_data_size"] = df_s10["kernel_input_data_size"]
df_s10_est["kernel_output_data_size"] = df_s10["kernel_output_data_size"]
df_s10_est["kernel_iterations"] = df_s10["kernel_iterations"]
df_s10_est["time_cpu"] = 0.0
df_s10_est["time_cpu_stddev"] = 0.0
df_s10_est["data_to_fpga_ocl"] = 0.0
df_s10_est["data_to_fpga_ocl_stddev"] = 0.0
df_s10_est["kernel_ocl"] = 0.0
df_s10_est["kernel_ocl_stddev"] = 0.0
df_s10_est["data_to_host_ocl"] = 0.0
df_s10_est["data_to_host_ocl_stddev"] = 0.0

print(df_s10_est)

est_filename = f"{common.data_rootdir}/{data_subdir}/s10-fast-estimated.csv"
print(f"Saving performance estimation to {est_filename}")
df_s10_est.to_csv(est_filename, index=False)
