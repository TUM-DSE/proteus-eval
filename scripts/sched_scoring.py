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
    def __init__(self, in_ports, out_ports, latency):
        """in_ports, out_ports: list of widths in bits"""
        self.in_ports = in_ports
        self.out_ports = out_ports
        # self.in_sizes = in_sizes
        # self.out_sizes = out_sizes
        self.latency = latency

kernels = {
    "cl_array_partition": Kernel([32, 32], [32], 4102),
    # "cl_burst_rw": Kernel([32], []),  # Result written back to input port
    "cl_burst_rw": Kernel([32], [32], 259),  # Result written back to input port
    "cl_dataflow_func": Kernel([32], [32], 131148),
    "cl_dataflow_subfunc": Kernel([32], [32], 131149),
    "cl_helloworld": Kernel([32, 32], [32], 259),
    "cl_lmem_2rw": Kernel([32, 32], [32], 1027),
    "cl_loop_reorder": Kernel([32, 32], [32], 4102),
    "cl_partition_cyclicblock": Kernel([32, 32], [32], 4103),
    "cl_shift_register": Kernel([32, 32], [32], 1048582),
    "cl_systolic_array": Kernel([32, 32], [32], 579),
    "cl_gmem_2banks": Kernel([512], [512], 5),
    # "cl_gmem_2banks_2x": Kernel([512, 512], [512, 512]),
    # "cl_gmem_2banks_4x": Kernel([512, 512, 512, 512], [512, 512, 512, 512]),
    # "cl_wide_mem_rw": Kernel([512, 512], [512]),
    "cl_wide_mem_rw_strm": Kernel([512, 512], [512], 132), # size: 512 * 16
    "cl_wide_mem_rw_2x": Kernel([512, 512, 512, 512], [512, 512], 132), # size: 512 * 16
    "cl_wide_mem_rw_4x": Kernel([512, 512, 512, 512, 512, 512, 512, 512], [512, 512, 512, 512], 132), # size: 512 * 16
    "3d-rendering": Kernel([32], [32], 261777),
    # "digit-recognition": Kernel([512, 512], [128]),
    "digit-recognition": Kernel([512, 512], [128], 441627152),
    "optical-flow": Kernel([512], [512], 449548),
    "spam-filter": Kernel([512, 32], [512], 3060556),
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
    df_freq = pd.read_csv("../data/frequencies_round_down.csv", skipinitialspace=True)
    df_max_freq = df_freq.iloc[:, 1:].max(axis=1)

    for i, app in enumerate(kernels.keys()):
        print(f"{app} -----------------------------------------------------------------------")
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
    
            print(f"{fpga}:")
            print(f"- freq: {freq} MHz")
            print(f"- best: {max_freq} MHz")
    
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
    df_freq = pd.read_csv("../data/frequencies_round_down.csv", skipinitialspace=True)
    df_max_freq = df_freq.iloc[:, 1:].max(axis=1)

    for i, app in enumerate(kernels.keys()):
        print(f"{app} -----------------------------------------------------------------------")
        # max_freq = df_max_freq.iloc[i]
        # max_freq = 200
        port_widths = kernels[app].in_ports + kernels[app].out_ports
        in_port_widths = kernels[app].in_ports
        out_port_widths = kernels[app].out_ports 
        kernel_latency = kernels[app].latency 
        thrps = {}
        kernel_lats = {}
        score_lats = {}
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
            # port_bandwidths = [(width * freq) / 8 for width in port_widths]
            # max_ports_per_channel = math.ceil(len(port_widths) / channels)
            
            # for mem-bound apps
            data_factor = 1.0
            if "wide_mem_rw" in app:
                data_factor = 16.0

            # CF for inputs
            # in_port_bandwidths = [(width * freq) / 8 for width in in_port_widths]
            in_port_bandwidths = [min((width * freq) / 8, (width * data_factor) * (freq / kernel_latency) ) for width in in_port_widths]
            max_input_ports_per_channel = math.ceil(len(in_port_widths) / channels)
            in_congestion_factors = [min(
                1, channel_bandwidth / (max_input_ports_per_channel * pbw)) for pbw in in_port_bandwidths]
            # if app == "digit-recognition" and fpga == "u280_ddr_fast":
            #     in_congestion_factors = [min(
            #         1, channel_bandwidth / (2 * pbw)) for pbw in in_port_bandwidths]

            # CF for outputs
            # out_port_bandwidths = [(width * freq) / 8 for width in out_port_widths]
            out_port_bandwidths = [min((width * freq) / 8, (width * data_factor) * (freq / kernel_latency) ) for width in out_port_widths]
            max_output_ports_per_channel = math.ceil(len(out_port_widths) / channels)
            out_congestion_factors = [min(
                1, channel_bandwidth / (max_output_ports_per_channel * pbw)) for pbw in out_port_bandwidths]

    
            # throughputs for each port
            in_port_thrps = [cf * pbw for cf,
                          pbw in zip(in_congestion_factors, in_port_bandwidths)]
            out_port_thrps = [cf * pbw for cf,
                          pbw in zip(out_congestion_factors, out_port_bandwidths)]

            # print(in_port_thrps)
            # print(out_port_thrps)

            # Latencies for each port
            in_port_lats = [x / y for x, y in zip(in_port_widths, in_port_thrps)] 
            out_port_lats = [x / y for x, y in zip(out_port_widths, out_port_thrps)]

            # print(in_port_lats)
            # print(out_port_lats)

            # get the max latency
            max_input_lat = max(in_port_lats)
            max_output_lat = max(out_port_lats)
            kernel_lats[fpga] = max(max_input_lat, max_output_lat)

            total_thrp = sum(in_port_thrps) + sum(out_port_thrps)
            thrps[fpga] = total_thrp
    
            # print(f"{fpga}:")
            print(f"- freq: {freq} MHz")
            # print(f"- port widths (bits): {port_widths}")
            print(f"-  input port bandwidths (MB/s): {in_port_bandwidths}")
            print(f"- output port bandwidths (MB/s): {out_port_bandwidths}")
            print(f"- max input ports per channel: {max_input_ports_per_channel}")
            print(f"- max output ports per channel: {max_output_ports_per_channel}")
            print(f"-  input congestion factors: {in_congestion_factors}")
            print(f"- output congestion factors: {out_congestion_factors}")
            print(f"-  input port throughputs (MB/s): {in_port_thrps}")
            print(f"- output port throughputs (MB/s): {out_port_thrps}")
            print(f"-  input port latency (s): {in_port_lats}")
            print(f"- output port latency (s): {out_port_lats}")
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
            # final_score = W_INPUT * (1/float(pcie_wr_bandwidth)) + W_KERNEL * (1/float(thrps[fpga])) + W_OUTPUT * (1/float(pcie_rd_bandwidth))
            final_score = (sum(in_port_widths)/float(pcie_wr_bandwidth)) + (kernel_lats[fpga]) + (sum(out_port_widths)/float(pcie_rd_bandwidth))
            # output_size_factor = sum(in_port_widths)/(640000/2000) if app == "digit-recognition" else sum(out_port_widths) # hints for digit-recognition (in_buf, out_buf) = (640000, 2000)

            # final_score = (sum(in_port_widths)/float(pcie_wr_bandwidth)) + (kernel_lats[fpga]) + (sum(out_port_widths)/float(pcie_rd_bandwidth))
            print(f"- {fpga}: ", final_score)
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

### Update app names
app_names = [key for key in kernels.keys()]
for i in range(len(app_names)):
    # skip Rosetta apps
    if app_names[i] == "3d-rendering":
        break

    app_names[i] = app_names[i][3:]
    if app_names[i] == "helloworld":
        app_names[i] = "vector_add"
    if app_names[i] == "wide_mem_rw_strm":
        app_names[i] = "wide_mem_rw"
print(app_names)

for i, key in enumerate(kernels.keys()):
    # range(len(app_names))
    df_old_scores = df_old_scores.rename(columns={key: app_names[i]})
    df_freq_scores = df_freq_scores.rename(columns={key: app_names[i]})
    df_new_scores = df_new_scores.rename(columns={key: app_names[i]})

print(df_old_scores)
print(df_freq_scores)
print(df_new_scores)

### Export the result to csv
filename_old  = "../sched_sim/scores_old.csv"
filename_freq = "../sched_sim/scores_freq.csv"
filename_new  = "../sched_sim/scores_new.csv"
print(f"\nSaving scores to {filename_old}, {filename_freq}, {filename_new}:")
df_old_scores.to_csv(filename_old, index=False)
df_freq_scores.to_csv(filename_freq, index=False)
df_new_scores.to_csv(filename_new, index=False)
