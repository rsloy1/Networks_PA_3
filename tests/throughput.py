#!/usr/bin/env python2
"""
Calculate throughput (in Mbps) from a log file that follows this format:

# queue: infinite
# base timestamp: 184
184 # 1504
184 # 1504
184 # 1504
185 # 1504
...

Each non-comment line contains:
   <timestamp> # <packet_size>

Usage:
    python2 throughput.py <log_file>
"""

import sys

def compute_throughput(log_file):
    total_bytes = 0
    timestamps = []

    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comment lines.
            if line.startswith("#"):
                continue
            parts = line.split()
            # Expect parts to look like: [timestamp, "#", packet_size]
            if len(parts) < 3:
                continue
            try:
                ts = float(parts[0])
                packet_size = int(parts[2])
            except ValueError:
                continue

            total_bytes += packet_size
            timestamps.append(ts)
    
    if not timestamps:
        print "No valid timestamps found in the log."
        return
    
    # Compute duration in seconds (timestamps are in milliseconds)
    duration_ms = max(timestamps) - min(timestamps)
    duration_sec = duration_ms / 1000.0
    if duration_sec <= 0:
        print "Invalid duration calculated."
        return
    
    throughput_mbps = (total_bytes * 8) / (duration_sec * 1e6)
    print("Total bytes: %d, Duration: %.2f s, Throughput: %.2f Mbps" % 
          (total_bytes, duration_sec, throughput_mbps))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python2 throughput.py <log_file>\n")
        sys.exit(1)
    compute_throughput(sys.argv[1])
