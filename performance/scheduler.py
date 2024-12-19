#!/usr/bin/env python3

import math
import pandas as pd


class Kernel:
    def __init__(self, in_ports, out_ports):
        """in_ports, out_ports: list of widths in bits"""
        self.in_ports = in_ports
        self.out_ports = out_ports


# Memory
HBM_CHANNEL_BANDWIDTH = 10_000
HBM_CHANNELS = 32
HBM_CAPACITY = 8_000
DDR_CHANNEL_BANDWIDTH = 15_000
DDR_CHANNELS = 2
DDR_CAPACITY = 32_000

# Weights
W_FREQ = 1/2
W_THRP = 1/2
W_MCAP = 0

kernels = {
    "cl_array_partition": Kernel([32, 32], [32]),
    "cl_burst_rw": Kernel([32], []),  # Result written back to input port
    "cl_dataflow_func": Kernel([32], [32]),
    "cl_dataflow_subfunc": Kernel([32], [32]),
    # Currently not in frequencies.csv
    # "cl_gmem_2banks": Kernel([512], [512]),
    "cl_helloworld": Kernel([32, 32], [32]),
    "cl_lmem_2rw": Kernel([32, 32], [32]),
    "cl_loop_reorder": Kernel([32, 32], [32]),
    "cl_partition_cyclicblock": Kernel([32, 32], [32]),
    "cl_shift_register": Kernel([32, 32], [32]),
    "cl_systolic_array": Kernel([32, 32], [32]),
    "cl_wide_mem_rw": Kernel([512, 512], [512]),
}

fpgas = ["u50_slow", "u50_fast", "u280_slow",
         "u280_fast", "u280_ddr_slow", "u280_ddr_fast"]

df_freq = pd.read_csv("../data/frequencies.csv", skipinitialspace=True)
df_max_freq = df_freq.iloc[:, 1:].max(axis=1)

for i, app in enumerate(kernels.keys()):
    print(f"{app} -----------------------------------------------------------------------")
    max_freq = df_max_freq.iloc[i]
    port_widths = kernels[app].in_ports + kernels[app].out_ports
    thrps = {}
    score_thrps = {}
    score_freqs = {}

    for fpga in fpgas:
        if "ddr" in fpga:
            channel_bandwidth = DDR_CHANNEL_BANDWIDTH
            channels = DDR_CHANNELS
        else:
            channel_bandwidth = HBM_CHANNEL_BANDWIDTH
            channels = HBM_CHANNELS

        freq = df_freq[f"{fpga}_freq"].iloc[i]
        score_freqs[fpga] = freq / max_freq

        # In MB/s
        port_bandwidths = [(width * freq) / 8 for width in port_widths]
        max_ports_per_channel = math.ceil(len(port_widths) / channels)
        congestion_factors = [min(
            1, channel_bandwidth / (max_ports_per_channel * pbw)) for pbw in port_bandwidths]

        port_thrps = [cf * pbw for cf,
                      pbw in zip(congestion_factors, port_bandwidths)]
        total_thrp = sum(port_thrps)
        thrps[fpga] = total_thrp

        print(f"{fpga}:")
        print(f"- freq: {freq} MHz")
        print(f"- port widths (bits): {port_widths}")
        print(f"- port bandwidths (MB/s): {port_bandwidths}")
        print(f"- max ports per channel: {max_ports_per_channel}")
        print(f"- congestion factors: {congestion_factors}")
        print(f"- port throughputs (MB/s): {port_thrps}")
        print(f"- total throughput (MB/s): {total_thrp}")

    max_thrp = max(thrps.values())
    print("Throughput scores:")
    for fpga in fpgas:
        score_thrps[fpga] = thrps[fpga] / max_thrp
        print(f"{fpga}: {score_thrps[fpga]}")

    print(f"Final scores (score_freq * {W_FREQ} + score_thrp * {W_THRP}, ignoring memory capacity for now):")
    for fpga in fpgas:
        print(f"{fpga}: ", score_freqs[fpga] * W_FREQ + score_thrps[fpga] * W_THRP)
