#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import sys

if len(sys.argv) < 5:
    sys.stderr.write("Usage: python2 generate_trace.py <bandwidth_mbps> <delay_ms> <duration_secs> <output_file>\n")
    sys.exit(1)

# Parse command-line arguments
bandwidth_mbps = float(sys.argv[1])      # e.g., 50 for 50 Mbps, 1 for 1 Mbps
delay_ms = float(sys.argv[2])            # e.g., 10 ms or 200 ms (not used in this simple simulation)
duration_secs = int(sys.argv[3])         # duration in seconds, e.g., 60
outfile = sys.argv[4]                    # output file path

# Calculate allowed bytes per millisecond
# For example, for 1 Mbps:
#   1 Mbps = 1,000,000 bits/sec → 1,000,000/1000 = 1000 bits per ms → 1000/8 = 125 bytes per ms.
bits_per_ms = (bandwidth_mbps * 1000000.0) / 1000.0
bytes_per_ms = bits_per_ms / 8.0

# Assume a standard packet size (MTU) of 1500 bytes.
packet_size = 1500.0  
accumulator = 0.0
trace = []

# For each millisecond of the experiment, accumulate available bytes.
# When enough bytes have accumulated to send a full packet, record the current timestamp (ms) and subtract the packet size.
for ms in range(duration_secs * 1000):
    accumulator += bytes_per_ms
    while accumulator >= packet_size:
        trace.append(ms)
        accumulator -= packet_size

# Write the trace to the specified output file.
with open(outfile, 'w') as f:
    for t in trace:
        f.write("%d\n" % t)

