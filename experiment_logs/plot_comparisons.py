#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt

# Determine base directory for experiment logs
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(script_dir) == 'experiment_logs':
    BASE_ROOT = script_dir
else:
    BASE_ROOT = os.path.join(script_dir, 'experiment_logs')

# --- CONFIGURATION --- #
SCHEMES = {
    "SCReAM": "1mbps_SCReAM",
    "LEDBAT": "1mbps_LEDBAT",
    "Tao":   "1mbps_Tao",
}

# Filenames
THROUGHPUT_LOG = "1mbps_datalink.log"
RTT_LOG        = "rttevents.log"
SENT_LOG       = "sent.log"
RECV_LOG       = "recv.log"

# --- LOADER HELPERS --- #
def load_throughput(path):
    ts, sizes = [], []
    if not os.path.isfile(path):
        return np.array([]), np.array([])
    with open(path) as f:
        for line in f:
            if line.startswith('#'): continue
            parts = line.strip().split()
            try:
                t = float(parts[0]) / 1000.0
                sz = int(parts[-1])
            except:
                continue
            ts.append(t)
            sizes.append(sz)
    if not ts:
        return np.array([]), np.array([])
    max_t = int(max(ts)) + 1
    bps = np.zeros(max_t)
    for t, sz in zip(ts, sizes):
        idx = int(t)
        if 0 <= idx < max_t:
            bps[idx] += sz
    return np.arange(len(bps)), (bps * 8) / 1e6


def load_loss(path_sent, path_recv):
    sent, recv = [], []
    if os.path.isfile(path_sent):
        with open(path_sent) as f:
            for line in f:
                if line.startswith('#'): continue
                try: sent.append(float(line.strip()))
                except: pass
    if os.path.isfile(path_recv):
        with open(path_recv) as f:
            for line in f:
                if line.startswith('#'): continue
                try: recv.append(float(line.strip()))
                except: pass
    if not sent or not recv:
        return np.array([]), np.array([])
    t0 = min(min(sent), min(recv))
    rel_sent = [t - t0 for t in sent]
    rel_recv = [t - t0 for t in recv]
    max_rel = max(rel_sent + rel_recv)
    max_t = int(max_rel) + 1
    sc = np.zeros(max_t)
    rc = np.zeros(max_t)
    for t in rel_sent:
        idx = int(t)
        if 0 <= idx < max_t: sc[idx] += 1
    for t in rel_recv:
        idx = int(t)
        if 0 <= idx < max_t: rc[idx] += 1
    loss = (sc - rc) / np.maximum(sc, 1) * 100.0
    return np.arange(len(loss)), loss


def load_rtt_stats(path):
    if not os.path.isfile(path):
        return None
    rtts = []
    with open(path) as f:
        for line in f:
            if line.startswith('#'): continue
            parts = line.strip().split()
            if len(parts) >= 3:
                try: rtts.append(float(parts[2]))
                except: pass
    if not rtts:
        return None
    a = np.array(rtts)
    return float(a.mean()), float(np.percentile(a, 95))

# --- PLOTTING --- #
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Throughput
ax = axes[0, 0]
for name, folder in SCHEMES.items():
    base = os.path.join(BASE_ROOT, folder)
    t, thr = load_throughput(os.path.join(base, THROUGHPUT_LOG))
    if t.size:
        ax.plot(t, thr, label=name)
if ax.get_legend_handles_labels()[0]:
    ax.legend()
ax.set_title('Time-series Throughput')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Throughput (Mbps)')

# Loss rate
ax = axes[0, 1]
for name, folder in SCHEMES.items():
    base = os.path.join(BASE_ROOT, folder)
    t, loss = load_loss(os.path.join(base, SENT_LOG), os.path.join(base, RECV_LOG))
    if t.size:
        ax.plot(t, loss, label=name)
if ax.get_legend_handles_labels()[0]:
    ax.legend()
ax.set_title('Time-series Loss Rate')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Loss Rate (%)')

# RTT bar chart
ax = axes[1, 0]
labels = []
avg_vals = []
p95_vals = []
for name, folder in SCHEMES.items():
    base = os.path.join(BASE_ROOT, folder)
    stats = load_rtt_stats(os.path.join(base, RTT_LOG))
    if stats:
        labels.append(name)
        avg, p95 = stats
        avg_vals.append(avg)
        p95_vals.append(p95)
if labels:
    x = np.arange(len(labels))
    width = 0.35
    ax.bar(x - width/2, avg_vals, width, label='Avg RTT')
    ax.bar(x + width/2, p95_vals, width, label='95th pct RTT')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
ax.set_title('RTT: Avg vs 95th percentile')
ax.set_ylabel('RTT (ms)')

# Scatter throughput vs RTT
ax = axes[1, 1]
for name, folder in SCHEMES.items():
    base = os.path.join(BASE_ROOT, folder)
    t, thr = load_throughput(os.path.join(base, THROUGHPUT_LOG))
    stats = load_rtt_stats(os.path.join(base, RTT_LOG))
    if stats and thr.size:
        mean_thr = float(thr.mean())
        mean_rtt, _ = stats
        ax.scatter(mean_rtt, mean_thr)
        ax.text(mean_rtt, mean_thr, ' '+name)
ax.set_title('Throughput vs RTT')
ax.set_xlabel('RTT (ms)')
ax.set_ylabel('Throughput (Mbps)')
ax.invert_xaxis()

plt.tight_layout()
plt.savefig(os.path.join(script_dir, 'comparison_plots.png'), dpi=150)
