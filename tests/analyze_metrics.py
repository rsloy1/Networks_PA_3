#!/usr/bin/env python2
"""
Analyze Experiment Metrics for Pantheon Experiments

This script calculates:
1. Throughput in Mbps from a log file containing lines like:
    <timestamp> # <packet_size>
2. Average RTT in milliseconds from an RTT log with lines:
    <send_timestamp> <ack_timestamp> <rtt_in_ms>
3. Packet Loss Rate by comparing a sent log and a received log where each line is a timestamp.

Usage:
    python2 analyze_metrics.py <throughput_log> <rttevents_log> <sent_log> <recv_log>

Example:
    python2 analyze_metrics.py experiment_logs/50mbps_datalink.log experiment_logs/rttevents.log experiment_logs/sent.log experiment_logs/recv.log
"""

import sys

def analyze_throughput(log_file):
    total_bytes = 0
    timestamps = []
    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                ts = float(parts[0])
                pkt_size = int(parts[2])
            except ValueError:
                continue
            total_bytes += pkt_size
            timestamps.append(ts)
    if not timestamps:
        return None
    # Assume timestamps are in milliseconds.
    duration_sec = (max(timestamps) - min(timestamps)) / 1000.0
    throughput_mbps = (total_bytes * 8) / (duration_sec * 1e6)
    return throughput_mbps, total_bytes, duration_sec

def analyze_rtt(rtt_file):
    rtt_samples = []
    with open(rtt_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                rtt = float(parts[2])
            except ValueError:
                continue
            rtt_samples.append(rtt)
    if not rtt_samples:
        return None
    avg_rtt = sum(rtt_samples) / len(rtt_samples)
    return avg_rtt, len(rtt_samples)

def analyze_loss(sent_file, recv_file):
    sent_count = sum(1 for line in open(sent_file) if line.strip() and not line.startswith("#"))
    recv_count = sum(1 for line in open(recv_file) if line.strip() and not line.startswith("#"))
    if sent_count == 0:
        return None
    loss_rate = (sent_count - recv_count) / float(sent_count)
    return loss_rate, sent_count, recv_count

def main():
    if len(sys.argv) != 5:
        sys.stderr.write("Usage: python2 analyze_metrics.py <throughput_log> <rttevents_log> <sent_log> <recv_log>\n")
        sys.exit(1)
    
    thr_result = analyze_throughput(sys.argv[1])
    rtt_result = analyze_rtt(sys.argv[2])
    loss_result = analyze_loss(sys.argv[3], sys.argv[4])
    
    if thr_result:
        thr, total, duration = thr_result
        print "Throughput: %.2f Mbps (Total bytes: %d, Duration: %.2f s)" % (thr, total, duration)
    else:
        print "No valid throughput data found."
    
    if rtt_result:
        avg_rtt, sample_count = rtt_result
        print "Average RTT: %.2f ms (from %d samples)" % (avg_rtt, sample_count)
    else:
        print "No valid RTT data found."
    
    if loss_result:
        loss_rate, sent_count, recv_count = loss_result
        print "Loss Rate: %.2f%% (Sent: %d, Received: %d)" % (loss_rate * 100, sent_count, recv_count)
    else:
        print "No valid loss data found."

if __name__ == '__main__':
    main()
