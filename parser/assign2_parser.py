# Parser for EE748 Assignment 2
# Yashas M Salian (yashas.msalian@iitb.ac.in)

import csv
import os
import sys

import pandas as pd

# Define some constant strings to identify relevant stats
ipc = "board.processor.switch2.core.ipc"
l1i_miss = "board.cache_hierarchy.l1i-cache-0.overallMissRate::total"
l1i_mpki = "board.cache_hierarchy.l1i-cache-0.overallMisses::total"
l1i_apki = "board.cache_hierarchy.l1i-cache-0.overallAccesses::total"
l1d_miss = "board.cache_hierarchy.l1d-cache-0.overallMissRate::total"
l1d_mpki = "board.cache_hierarchy.l1d-cache-0.overallMisses::total"
l1d_apki = "board.cache_hierarchy.l1d-cache-0.overallAccesses::total"
l2_miss = "board.cache_hierarchy.l2-cache-0.overallMissRate::total"
l2_mpki = "board.cache_hierarchy.l2-cache-0.overallMisses::total"
l2_apki = "board.cache_hierarchy.l2-cache-0.overallAccesses::total"

# Switch to directory of interest
os.chdir(sys.argv[1])

# Define header
header = [
    "Benchmark",
    "IPC",
    "L1I Miss Rate",
    "L1I MPKI",
    "L1I APKI",
    "L1D Miss Rate",
    "L1D MPKI",
    "L1D APKI",
    "L2 Miss Rate",
    "L2 MPKI",
    "L2 APKI",
]

# Define list to hold stats
stats_list = []
stats_list.append(header)

# Iterate through all subdirectories
for subdirectory in os.listdir():
    # Move to subdirectory
    os.chdir(subdirectory)

    # Create list to store stats in
    stats_row = []

    # Read stats.txt into a pandas dataframe
    stats_df = pd.read_table("stats.txt")

    # Split table into columns
    stats_df = stats_df[
        "---------- Begin Simulation Statistics ----------"
    ].str.split(n=2, expand=True)

    # Add each stat to the stats_row list
    stats_row.append(subdirectory)
    stats_row.append(float(stats_df.loc[stats_df[0] == ipc][1]))

    if l1i_miss in stats_df[0].values:
        stats_row.append(float(stats_df.loc[stats_df[0] == l1i_miss][1]))
    else:
        stats_row.append(0.0)

    if l1i_mpki in stats_df[0].values:
        stats_row.append(
            float(stats_df.loc[stats_df[0] == l1i_mpki][1]) / 50000
        )
    else:
        stats_row.append(0.0)

    if l1i_apki in stats_df[0].values:
        stats_row.append(
            float(stats_df.loc[stats_df[0] == l1i_apki][1]) / 50000
        )
    else:
        stats_row.append(0.0)

    if l1d_miss in stats_df[0].values:
        stats_row.append(float(stats_df.loc[stats_df[0] == l1d_miss][1]))
    else:
        stats_row.append(0.0)

    if l1d_mpki in stats_df[0].values:
        stats_row.append(
            float(stats_df.loc[stats_df[0] == l1d_mpki][1]) / 50000
        )
    else:
        stats_row.append(0.0)

    if l1d_apki in stats_df[0].values:
        stats_row.append(
            float(stats_df.loc[stats_df[0] == l1d_apki][1]) / 50000
        )
    else:
        stats_row.append(0.0)

    if l2_miss in stats_df[0].values:
        stats_row.append(float(stats_df.loc[stats_df[0] == l2_miss][1]))
    else:
        stats_row.append(0.0)

    if l2_mpki in stats_df[0].values:
        stats_row.append(
            float(stats_df.loc[stats_df[0] == l2_mpki][1]) / 50000
        )
    else:
        stats_row.append(0.0)

    if l2_apki in stats_df[0].values:
        stats_row.append(
            float(stats_df.loc[stats_df[0] == l2_apki][1]) / 50000
        )
    else:
        stats_row.append(0.0)

    stats_list.append(stats_row)

    # Revert to previous directory
    os.chdir("..")


print(stats_list)

# Write stats to a CSV file in the same directory
with open("stats.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(stats_list)
