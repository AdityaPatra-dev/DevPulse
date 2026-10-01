#!/usr/bin/env bash
# Disk monitoring cron script for Ubuntu Server
# Records timestamp and root partition disk usage to /var/log/devpulse_disk_usage.log

LOG_FILE="/var/log/devpulse_disk_usage.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5 " used (" $3 "/" $2 ")"}')

echo "[${TIMESTAMP}] DISK USAGE: ${DISK_USAGE}" >> "${LOG_FILE}"
