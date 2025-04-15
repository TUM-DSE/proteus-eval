#!/usr/bin/env python3

import common
import pandas as pd
import numpy as np

df = pd.read_csv(f"{common.data_rootdir}/loc.csv", skipinitialspace=True)

df_apps = df[df["File"].str.contains("host.cpp")]
df_lib = df[~df["File"].str.contains("host.cpp")]

print("Changes for common lib:")
print(df_lib.iloc[:, 1:].sum())
