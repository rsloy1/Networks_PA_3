#!/usr/bin/env python2
"""
Dummy Tunnel Client for Pantheon Auto-Test Mode.

This script reads commands from stdin interactively using raw_input()
and immediately echoes "ACK" to stdout. Debug info is printed to stderr.
"""
import sys, time

while True:
    try:
        line = raw_input("> ")  # Prompts with "> " and waits for user input
    except EOFError:
        break
    # Immediately output ACK
    time.sleep(0.2)
    sys.stdout.write("ACK\n")
    sys.stdout.flush()

