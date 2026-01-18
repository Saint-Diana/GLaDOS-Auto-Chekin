#!/bin/bash
# GLaDOS Auto Check-in Startup Script

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Log file with date
LOG_FILE="checkin_$(date +%Y%m%d).log"

# Activate conda environment and run script
echo "========================================" | tee -a "$LOG_FILE"
echo "GLaDOS Auto Check-in - $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Source conda and activate environment
source /home/shen/Work/Environment/Anaconda3/etc/profile.d/conda.sh
conda activate glados-checkin

# Run Python script
python glados_checkin.py 2>&1 | tee -a "$LOG_FILE"

echo "Check-in completed at $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
