#!/bin/bash
read -p "Command: " cmd
if [[ "$cmd" =~ "pip install" || "$cmd" =~ "python -m" ]]; then
    read -p "Risky command detected. Confirm? (y/N) " confirm
    [[ "$confirm" == "y" ]] || { echo "Aborted."; exit 1; }
fi
eval "$cmd" | tee output.log
read -p "Paste output to chat? (y/N) " paste
[[ "$paste" == "y" ]] && cat output.log
