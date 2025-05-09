import os
import inspect
import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import pandas as pd
import seaborn as sns  # type: ignore


bar_blue = '#8EA9DB'
bar_orange = '#F4B084'
bar_green = '#99d8c9'
bar_brown = '#d8b365'
bar_grey = '#aeb6bf'
bar_purple = '#c070ff'

script_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
script_dir = os.path.dirname(script_path)
plot_dir = f"{script_dir}/../plots"
data_rootdir = f"{script_dir}/../data"

app_names_abb = {
        "array_partition": "ar_part",
        "burst_rw": "b_rw",
        "dataflow_func": "df_func",
        "dataflow_subfunc": "df_subf",
        "helloworld": "vadd",
        "lmem_2rw": "lmem",
        "loop_reorder": "loop_rr",
        "partition_cyclicblock": "par_cyc",
        "shift_register": "sft_reg",
        "systolic_array": "sys_ar",
        "gmem_2banks": "gmem",
        "wide_mem_rw": "wmem",
        "wide_mem_rw_strm": "wmem_st",
        "3d-rendering": "3d-rndr",
        "digit-recognition": "dgt-rc",
        "optical-flow": "opt-fl",
        "spam-filter": "sp-fltr",
        "wide_mem_rw_2x": "wmem2x",
        "wide_mem_rw_4x": "wmem4x",
        "gmem_2banks_2x": "gmem2x",
        "gmem_2banks_4x": "gmem4x",
        "vector_add": "vadd",
        "average": "avg",
        }

def get_value(filename, x):
    fileObj = open(filename, "r")  # opens the file in read mode
    words = fileObj.read().splitlines()  # puts the file into an array
    fileObj.close()
    print(x)
    val = words[x]
    val_int = float(val)
    print(val_int)
    return val_int


def get_average(filename):
    fileObj = open(filename, "r")  # opens the file in read mode
    words = fileObj.read().splitlines()  # puts the file into an array
    nums = np.array([float(numeric_string) for numeric_string in words])
    fileObj.close()
    return np.mean(nums)
