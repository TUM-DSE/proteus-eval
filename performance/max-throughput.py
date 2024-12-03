#!/usr/bin/env python3

import pandas as pd

df_u50 = pd.read_csv("../data/u50-metadata.csv", skipinitialspace=True)
df_u280 = pd.read_csv("../data/u280-metadata.csv", skipinitialspace=True)
df_result = pd.DataFrame(df_u50["app_name"])

df_result["u50_max_throughput"] = df_u50.apply(
    lambda row: (row["kernel_input_bus_width"] / 8) * row["faster_frequency"], axis=1)

df_result["u280_max_throughput"] = df_u280.apply(
    lambda row: (row["kernel_input_bus_width"] / 8) * row["faster_frequency"], axis=1)

df_result["u280_ddr_max_throughput"] = df_u280.apply(
    lambda row: (row["kernel_input_bus_width"] / 8) * row["ddr_faster_frequency"], axis=1)

filename = "throughput.csv"
print(f"Saving data to {filename}")
df_result.to_csv(filename, index=False)
