#!/bin/bash
# Helper script to monitor OTP codes in real-time

echo "========================================="
echo "   OTP CODE MONITOR (For Testing)"
echo "========================================="
echo ""
echo "Watching for OTP codes in backend logs..."
echo "Press Ctrl+C to stop"
echo ""

# Watch backend logs and filter for OTP-related messages
tail -f /var/log/supervisor/backend.out.log | grep --line-buffered -E "(OTP created|session:|User registered)" | while read line; do
    echo "[$(date '+%H:%M:%S')] $line"
done
