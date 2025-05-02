#!/usr/bin/env python3

import math
import pandas as pd

### Define FPGA-specific parameters
# bandwidths are roughly measured by 'xbutil validate'
# Memory
HBM_CHANNEL_BANDWIDTH = 12_400  # MB/s
HBM_CHANNELS = 32
HBM_CAPACITY = 8_000
DDR_CHANNEL_BANDWIDTH = 17_000  # MB/s
DDR_CHANNELS = 2
DDR_CAPACITY = 32_000

# PCIe
PCIE_HBM_WR_BANDWIDTH = 11_500
PCIE_HBM_RD_BANDWIDTH = 11_500
PCIE_DDR_WR_BANDWIDTH = 8_500
PCIE_DDR_RD_BANDWIDTH = 11_500

# Weights
W_FREQ = 1/2
W_THRP = 1/2
W_MCAP = 0

W_INPUT = 1
W_KERNEL = 1
W_OUTPUT = 1

### Define metadata of FPGA kernels
class Kernel:
    def __init__(self, in_ports, out_ports):
        """in_ports, out_ports: list of widths in bits"""
        self.in_ports = in_ports
        self.out_ports = out_ports

kernels = {
    "cl_array_partition": Kernel([32, 32], [32]),
    "cl_burst_rw": Kernel([32], []),  # Result written back to input port
    "cl_dataflow_func": Kernel([32], [32]),
    "cl_dataflow_subfunc": Kernel([32], [32]),
    "cl_helloworld": Kernel([32, 32], [32]),
    "cl_lmem_2rw": Kernel([32, 32], [32]),
    "cl_loop_reorder": Kernel([32, 32], [32]),
    "cl_partition_cyclicblock": Kernel([32, 32], [32]),
    "cl_shift_register": Kernel([32, 32], [32]),
    "cl_systolic_array": Kernel([32, 32], [32]),
    "cl_gmem_2banks": Kernel([512], [512]),
    # "cl_wide_mem_rw": Kernel([512, 512], [512]),
    "cl_wide_mem_rw_strm": Kernel([512, 512], [512]),
    "cl_wide_mem_rw_2x": Kernel([512, 512], [512]),
    "cl_wide_mem_rw_4x": Kernel([512, 512], [512]),
}

### Define FPGA types
# fpgas = ["u50_slow", "u280_slow", "u280_ddr_slow",
#          "u50_fast", "u280_fast", "u280_ddr_fast"]
fpgas = ["u50_fast", "u280_fast", "u280_ddr_fast"]
# fpgas = ["u50_slow", "u280_slow", "u280_ddr_slow"]

### Define scoring functions: old, new, freq-only
def scoring_old(df_scores):
    df_freq = pd.read_csv("../data/frequencies.csv", skipinitialspace=True)
    df_max_freq = df_freq.iloc[:, 1:].max(axis=1)

    for i, app in enumerate(kernels.keys()):
        # print(f"{app} -----------------------------------------------------------------------")
        max_freq = df_max_freq.iloc[i]
        # max_freq = 200
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
    
            # print(f"{fpga}:")
            # print(f"- freq: {freq} MHz")
            # print(f"- port widths (bits): {port_widths}")
            # print(f"- port bandwidths (MB/s): {port_bandwidths}")
            # print(f"- max ports per channel: {max_ports_per_channel}")
            # print(f"- congestion factors: {congestion_factors}")
            # print(f"- port throughputs (MB/s): {port_thrps}")
            # print(f"- total throughput (MB/s): {total_thrp}")
    
        max_thrp = max(thrps.values())
        # print("Throughput scores:")
        for fpga in fpgas:
            score_thrps[fpga] = thrps[fpga] / max_thrp
            # print(f"- {fpga}: {score_thrps[fpga]}")
    
        # print(f"Final scores (score_freq * {W_FREQ} + score_thrp * {W_THRP}, "
        #       "ignoring memory capacity for now):")
        tmp_list = []
    
        for fpga in fpgas:
            final_score = score_freqs[fpga] * W_FREQ + score_thrps[fpga] * W_THRP
            # print(f"- {fpga}: ", final_score)
            # print(f"{fpga}: ", score_freqs[fpga] * W_FREQ + score_thrps[fpga] * W_THRP)
            tmp_list.insert(len(tmp_list), final_score)
    
        df_scores[app] = tmp_list

    return df_scores

### Freq-only scoring function
def scoring_freq(df_scores):
    df_freq = pd.read_csv("../data/frequencies.csv", skipinitialspace=True)
    df_max_freq = df_freq.iloc[:, 1:].max(axis=1)

    for i, app in enumerate(kernels.keys()):
        # print(f"{app} -----------------------------------------------------------------------")
        max_freq = df_max_freq.iloc[i]
        # max_freq = 200
        port_widths = kernels[app].in_ports + kernels[app].out_ports
        thrps = {}
        score_thrps = {}
        score_freqs = {}
    
        for fpga in fpgas:
            ### Scoring clock frequency
            freq = df_freq[f"{fpga}_freq"].iloc[i]
            score_freqs[fpga] = freq / max_freq
    
            # print(f"{fpga}:")
            # print(f"- freq: {freq} MHz")
    
        # print(f"Final scores (score_freq only):")
        tmp_list = []
    
        for fpga in fpgas:
            final_score = score_freqs[fpga]
            # print(f"- {fpga}: ", final_score)
            # print(f"{fpga}: ", score_freqs[fpga] * W_FREQ + score_thrps[fpga] * W_THRP)
            tmp_list.insert(len(tmp_list), final_score)
    
        df_scores[app] = tmp_list

    return df_scores



### New scoring functions
def scoring_new(df_scores):
    df_freq = pd.read_csv("../data/frequencies.csv", skipinitialspace=True)
    df_max_freq = df_freq.iloc[:, 1:].max(axis=1)

    for i, app in enumerate(kernels.keys()):
        # print(f"{app} -----------------------------------------------------------------------")
        # max_freq = df_max_freq.iloc[i]
        # max_freq = 200
        port_widths = kernels[app].in_ports + kernels[app].out_ports
        thrps = {}
        score_thrps = {}
        score_freqs = {}
    
        ### Calculate the kernel's throughput
        for fpga in fpgas:
            # distinguish DDR and HBM 
            if "ddr" in fpga:
                channel_bandwidth = DDR_CHANNEL_BANDWIDTH
                channels = DDR_CHANNELS
                pcie_wr_bandwidth = PCIE_DDR_WR_BANDWIDTH
                pcie_rd_bandwidth = PCIE_DDR_RD_BANDWIDTH
            else:
                channel_bandwidth = HBM_CHANNEL_BANDWIDTH
                channels = HBM_CHANNELS
                pcie_wr_bandwidth = PCIE_HBM_WR_BANDWIDTH
                pcie_rd_bandwidth = PCIE_HBM_RD_BANDWIDTH
    
            # get CPU freq
            freq = df_freq[f"{fpga}_freq"].iloc[i]

            # In MB/s
            port_bandwidths = [(width * freq) / 8 for width in port_widths]
            max_ports_per_channel = math.ceil(len(port_widths) / channels)
            congestion_factors = [min(
                1, channel_bandwidth / (max_ports_per_channel * pbw)) for pbw in port_bandwidths]
    
            port_thrps = [cf * pbw for cf,
                          pbw in zip(congestion_factors, port_bandwidths)]
            total_thrp = sum(port_thrps)
            thrps[fpga] = total_thrp
    
            # print(f"{fpga}:")
            # print(f"- freq: {freq} MHz")
            # print(f"- port widths (bits): {port_widths}")
            # print(f"- port bandwidths (MB/s): {port_bandwidths}")
            # print(f"- max ports per channel: {max_ports_per_channel}")
            # print(f"- congestion factors: {congestion_factors}")
            # print(f"- port throughputs (MB/s): {port_thrps}")
            # print(f"- total throughput (MB/s): {total_thrp}")
    
        max_thrp = max(thrps.values())
        # print("Throughput scores:")
        for fpga in fpgas:
            score_thrps[fpga] = thrps[fpga] / max_thrp
            # print(f"- {fpga}: {score_thrps[fpga]}")
    
        # print(f"Final scores ({W_INPUT} * input_time + {W_KERNEL} * kernel_time + {W_OUTPUT} * output_time):")
        tmp_list = []
        highest_score = 0.0
        # (non-stream processing only for now)
        # (1/PCIe write thrp.) + (1/kernel thrp.) + (1/PCIe read thrp.)
        for fpga in fpgas:
            final_score = W_INPUT * (1/float(pcie_wr_bandwidth)) + W_KERNEL * (1/float(thrps[fpga])) + W_OUTPUT * (1/float(pcie_rd_bandwidth))
            # print(f"- {fpga}: ", final_score)
            # print(f"{fpga}: ", score_freqs[fpga] * W_FREQ + score_thrps[fpga] * W_THRP)
            tmp_list.insert(len(tmp_list), final_score)
            if final_score > highest_score: # lower is better
                highest_score = final_score

        relative_list = []
        for score in tmp_list:
            relative_score = score/highest_score
            relative_list.insert(len(relative_list), relative_score)
    
        df_scores[app] = relative_list

    return df_scores


### Scoring (old)
df_old_scores = pd.DataFrame({"fpgas": fpgas})
df_old_scores = scoring_old(df_old_scores)
print(df_old_scores)

### Scoring (freq-only)
df_freq_scores = pd.DataFrame({"fpgas": fpgas})
df_freq_scores = scoring_freq(df_freq_scores)
print(df_freq_scores)

### Scoring (new)
df_new_scores = pd.DataFrame({"fpgas": fpgas})
df_new_scores = scoring_new(df_new_scores)
print(df_new_scores)

### Export the result to csv
filename_old  = "../sched_sim/scores_old.csv"
filename_freq = "../sched_sim/scores_freq.csv"
filename_new  = "../sched_sim/scores_new.csv"
print(f"\nSaving scores to {filename_old}, {filename_freq}, {filename_new}:")
df_old_scores.to_csv(filename_old, index=False)
df_freq_scores.to_csv(filename_freq, index=False)
df_new_scores.to_csv(filename_new, index=False)
