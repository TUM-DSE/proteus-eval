#!/usr/bin/env python3
import pandas as pd


u50_slow = pd.read_csv("../data/u50-slow-vitis.csv", skipinitialspace=True)
u280_slow = pd.read_csv("../data/u280-slow-vitis.csv", skipinitialspace=True)
u280_ddr_slow = pd.read_csv("../data/u280-ddr-slow-vitis.csv", skipinitialspace=True)
u50_fast = pd.read_csv("../data/u50-fast-vitis.csv", skipinitialspace=True)
u280_fast = pd.read_csv("../data/u280-fast-vitis.csv", skipinitialspace=True)
u280_ddr_fast = pd.read_csv("../data/u280-ddr-fast-vitis.csv", skipinitialspace=True)

apps = [
    "cl_array_partition",
    "cl_burst_rw",
    "cl_dataflow_func",
    "cl_dataflow_subfunc",
    "cl_helloworld",
    "cl_lmem_2rw",
    "cl_loop_reorder",
    "cl_partition_cyclicblock",
    "cl_shift_register",
    "cl_systolic_array",
    "cl_wide_mem_rw"
]

for app in apps:
    print(app)

    app_u50_slow = u50_slow.loc[u50_slow["app_name"] == app]
    app_u50_slow_cp = app_u50_slow.copy()
    app_u50_slow_cp.loc[:, "total_fpga_time"] = app_u50_slow_cp.iloc[:, -3:].sum(axis=1)

    app_u280_slow = u280_slow.loc[u280_slow["app_name"] == app]
    app_u280_slow_cp = app_u280_slow.copy()
    app_u280_slow_cp.loc[:, "total_fpga_time"] = app_u280_slow_cp.iloc[:, -3:].sum(axis=1)

    app_u280_ddr_slow = u280_ddr_slow.loc[u280_ddr_slow["app_name"] == app]
    app_u280_ddr_slow_cp = app_u280_ddr_slow.copy()
    app_u280_ddr_slow_cp.loc[:, "total_fpga_time"] = app_u280_ddr_slow_cp.iloc[:, -3:].sum(axis=1)

    app_u50_fast = u50_fast.loc[u50_fast["app_name"] == app]
    app_u50_fast_cp = app_u50_fast.copy()
    app_u50_fast_cp.loc[:, "total_fpga_time"] = app_u50_fast_cp.iloc[:, -3:].sum(axis=1)

    app_u280_fast = u280_fast.loc[u50_fast["app_name"] == app]
    app_u280_fast_cp = app_u280_fast.copy()
    app_u280_fast_cp.loc[:, "total_fpga_time"] = app_u280_fast_cp.iloc[:, -3:].sum(axis=1)

    app_u280_ddr_fast = u280_ddr_fast.loc[u50_fast["app_name"] == app]
    app_u280_ddr_fast_cp = app_u280_ddr_fast.copy()
    app_u280_ddr_fast_cp.loc[:, "total_fpga_time"] = app_u280_ddr_fast_cp.iloc[:, -3:].sum(axis=1)

    df_result = pd.concat([app_u50_slow_cp, app_u280_slow_cp, app_u280_ddr_slow_cp,
                           app_u50_fast_cp, app_u280_fast_cp, app_u280_ddr_fast_cp], axis=0, ignore_index=True)

    header = ["u50_slow", "u280_slow", "u280_ddr_slow", "u50_fast", "u280_fast", "u280_ddr_fast"]
    df_result.insert(1, 'bs_type', header)
    # df_result = df_result.drop('app_name', axis=1)

    print(df_result)

    # Export the result to csv
    # filename = f"{app}.csv"
    # print(f"Saving data to {filename}")
    # df_result.to_csv(filename, index=False)
