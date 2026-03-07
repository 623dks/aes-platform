#!/bin/bash
source /home/g623dks/miniconda/etc/profile.d/conda.sh
conda activate aes-llama-310
sudo kill -9 $(sudo lsof /dev/nvidia0 2>/dev/null | awk 'NR>1 {print $2}' | sort -u) 2>/dev/null
sleep 3
cd /home/g623dks
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1 2>&1 | tee /home/g623dks/backend.log &
echo "Backend starting..."
