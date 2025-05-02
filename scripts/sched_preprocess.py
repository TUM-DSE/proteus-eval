#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics as stat
import common

df_u50_slow      = pd.read_csv(f"../data/proteus/u50-slow.csv", skipinitialspace=True)
df_u280_slow     = pd.read_csv(f"../data/proteus/u280-slow.csv", skipinitialspace=True)
df_u280_ddr_slow = pd.read_csv(f"../data/proteus/u280-ddr-slow.csv", skipinitialspace=True)
df_u50_fast      = pd.read_csv(f"../data/proteus/u50-fast.csv", skipinitialspace=True)
df_u280_fast     = pd.read_csv(f"../data/proteus/u280-fast.csv", skipinitialspace=True)
df_u280_ddr_fast = pd.read_csv(f"../data/proteus/u280-ddr-fast.csv", skipinitialspace=True)

# dfs = [df_u50_slow, df_u50_fast, df_u280_slow, df_u280_fast, df_u280_ddr_slow, df_u280_ddr_fast]
# dfs = [df_u50_slow, df_u280_slow, df_u280_ddr_slow, df_u50_fast, df_u280_fast, df_u280_ddr_fast]
dfs = [df_u50_fast, df_u280_fast, df_u280_ddr_fast]
df_labels = ["u50-hbm", "u280-hbm", "u280-ddr"]

df_app_name = dfs[0]["app_name"].copy()
app_names = df_app_name.values
print(app_names)


for app in app_names:
    # skip wide_mem_rw
    if app == "cl_wide_mem_rw":
        continue

    # make df for each app
    found_rows = []
    i = 0
    for df in dfs: 
        row = df[df["app_name"] == app]
        row.loc[:, "app_name"] = df_labels[i] # clarify that we modify only the filtered df
        # row["app_name"] = df_labels[i]
        found_rows.append(row)
        i+=1

    df_app = pd.concat(found_rows, ignore_index=True)

    # export df to a file
    app_file = app[3:]
    if app_file == "helloworld":
        app_file = "vector_add"
    if app_file == "wide_mem_rw_strm":
        app_file = "wide_mem_rw"

    filename = f"../sched_sim/{app_file}.csv"

    df_app.to_csv(filename, index=False)
    print(df_app)

# exit(0)

# Remove cl_wide_mem_rw and cl_
# for i in range(len(app_names)): 
#     if app_names[i] == "cl_wide_mem_rw":
#         matched_id = i
#     else:
#         app_names[i] = app_names[i][3:]
# app_names = np.delete(app_names, matched_id)
# print(app_names)
# print(df_u50_slow)

# Remove _strm, change hello_world name
# for i in range(len(app_names)):
#     if app_names[i] == "helloworld":
#         app_names[i] = "vector_add"
#     if app_names[i] == "wide_mem_rw_strm":
#         app_names[i] = "wide_mem_rw"

