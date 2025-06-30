#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instrumentum Script: inponere_arnanebtarium (Place in Armory)
Version: 1.0.0.L
Role: A safe, user-facing tool to upload or update a Manipulus script
      in the correct Arnanebtarium folder on GitHub.
"""
import sys
import argparse
import json
import subprocess
import os

# --- Configuration ---
ARMA_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "arma_repository.py")
DEFAULT_BOT_USER = "Isidore@DecanusBot" # Not used for GitHub, but good practice

FOLDER_MAP = {
    "approved": "Arnanebtarium/Licet_Agere",      # "It is permitted to act"
    "pending": "Arnanebtarium/Sub_Iudice",       # "Under judgment"
    "denied": "Arnanebtarium/Noli_Agere",        # "Do not act"
    "reserved": "Arnanebtarium/Arma_Reservata"  # "Reserved Arms"
}

def main():
    parser = argparse.ArgumentParser(description="Uploads a tool script to the GitHub Arnanebtarium.")
    parser.add_argument('local_path', help="The local path to the script file to be uploaded.")
    parser.add_argument('status', choices=FOLDER_MAP.keys(), help="The status of the tool, determining its destination folder.")
    args = parser.parse_args()

    if not os.path.exists(args.local_path):
        print(f"Error: Local file not found at '{args.local_path}'", file=sys.stderr)
        sys.exit(1)

    # --- FIDUCIA SAGA PLACEHOLDER ---
    # In a future Centurion-led operation, this is where the DEPOSITUM step would occur.
    # A Quaestor would be alerted to monitor this transaction.
    # An echo would confirm the PENDING status before proceeding.
    print(f"INFO: Preparing to place '{os.path.basename(args.local_path)}' in '{FOLDER_MAP[args.status]}'.")

    try:
        with open(args.local_path, 'r', encoding='utf-8') as f:
            content = f.read()

        repo_path = f"{FOLDER_MAP[args.status]}/{os.path.basename(args.local_path)}"
        commit_message = f"ARNANEBTARIUM: Update/Create {os.path.basename(args.local_path)} in {args.status}."
        
        # Construct the JSON command for the Arma
        command_data = {
            "action": "repository_push",
            "parameters": {
                "repo_path": repo_path,
                "content": content,
                "commit_message": commit_message
            }
        }

        # Dispatch to the Arma
        process = subprocess.Popen(
            ['python3', ARMA_SCRIPT_PATH],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate(json.dumps(command_data))

        if process.returncode != 0:
            print("\n--- CRITICAL ARMA FAILURE ---")
            print(stderr.strip())
            print("----------------------------")
        else:
            print("\n--- ARMA REPORT ---")
            print(json.dumps(json.loads(stdout), indent=2))
            print("-------------------")

        # --- FIDUCIA SAGA PLACEHOLDER ---
        # Here, the Centurion would receive the echo and perform the FINALIZE step,
        # updating the Depositum in the Acta Diurna to SUCCESS or FAILURE.

    except Exception as e:
        print(f"An unexpected error occurred in the orchestrator: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
