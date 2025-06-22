#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AIOps Toolkit: Automated VLOR Backup Utility
# Version: 4.2.0 (Token Expiration Reminder)
#
# This script dynamically discovers VLORs by querying two specific
# MediaWiki categories. It then creates a new branch, commits the changes,
# and opens a pull request for human review.

import os
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv
import pywikibot
import re

# --- CONFIGURATION ---
REPO_PATH = os.path.expanduser('~/Isidore-Operations-MCT')
VLOR_FOLDER_NAME = 'VLORs'
ENV_FILE_PATH = os.path.expanduser('~/aiops_toolkit/.env.vlor_backup')
DISCOVERY_CATEGORIES = ['Category:Initiative VLOR', 'Category:Operation VLOR']

def get_vlor_pages_from_categories(site):
    """Reads wiki categories to get a list of VLOR pages."""
    all_vlor_pages = []
    page_titles = set() # Use a set to avoid duplicates

    print(f"Querying for pages in {len(DISCOVERY_CATEGORIES)} categories...")
    for cat_name in DISCOVERY_CATEGORIES:
        vlor_category = pywikibot.Category(site, cat_name)
        pages = list(vlor_category.articles())
        for page in pages:
            if page.title() not in page_titles:
                all_vlor_pages.append(page)
                page_titles.add(page.title())
        print(f"  - Found {len(pages)} pages in '{cat_name}'.")
    
    print(f"Total unique VLOR pages found: {len(all_vlor_pages)}.")
    return all_vlor_pages

def generate_filename_from_title(title):
    """
    Creates a safe filename from a wiki page title.
    Example: 'OODA WIKI:WikiProject Isidore/Michael/VLOR' -> 'Isidore_Michael.mw'
    """
    # Normalize spaces for consistency
    title = title.replace(' ', '_')
    match = re.search(r'WikiProject_([^/]+)/([^/]+)/VLOR', title)
    if match:
        project = match.group(1)
        operation = match.group(2)
        return f"{project}_{operation}.mw"
    else:
        # Fallback for Initiative VLORs or other formats
        # Example: 'OODA_WIKI:WikiProject_Isidore/VLOR' -> 'Isidore_Initiative.mw'
        match_initiative = re.search(r'WikiProject_([^/]+)/VLOR', title)
        if match_initiative:
            project = match_initiative.group(1)
            return f"{project}_Initiative.mw"
        else:
            # Generic fallback
            return title.replace(':', '_').replace('/', '_') + ".mw"

def run_command(command, cwd, env=None):
    """Executes a shell command and handles errors."""
    print(f"Executing: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd, env=env)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(result.stdout)
    return result

def main():
    """Main execution function."""
    # --- Token Expiration Reminder ---
    # This check provides a high-visibility reminder in the logs.
    print("="*60)
    print("REMINDER: The GitHub Personal Access Token used by this script")
    print("          has a 90-day expiration. Please ensure it is valid.")
    print("="*60)
    
    print(f"--- Starting Category-Based VLOR Backup @ {datetime.now()} ---")
    
    load_dotenv(dotenv_path=ENV_FILE_PATH)
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print(f"ERROR: GITHUB_TOKEN not found in {ENV_FILE_PATH}", file=sys.stderr)
        sys.exit(1)

    site = pywikibot.Site()
    site.login()
    vlor_pages = get_vlor_pages_from_categories(site)
    
    timestamp = datetime.now().strftime('%Y-%m-%d-%H%M')
    branch_name = f"auto-backup/{timestamp}"
    
    run_command(['git', 'fetch', 'origin'], cwd=REPO_PATH)
    run_command(['git', 'checkout', 'origin/main', '-b', branch_name], cwd=REPO_PATH)
    
    target_dir = os.path.join(REPO_PATH, VLOR_FOLDER_NAME)
    os.makedirs(target_dir, exist_ok=True)

    for page in vlor_pages:
        file_name = generate_filename_from_title(page.title())
        file_path = os.path.join(target_dir, file_name)
        print(f"Backing up '{page.title()}' to '{file_name}'...")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(page.text)
    
    run_command(['git', 'add', f'{VLOR_FOLDER_NAME}/'], cwd=REPO_PATH)
    
    status_result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=REPO_PATH)
    if not status_result.stdout.strip():
        print("No changes detected since last backup. Cleaning up branch and exiting.")
        run_command(['git', 'checkout', 'main'], cwd=REPO_PATH)
        run_command(['git', 'branch', '-D', branch_name], cwd=REPO_PATH)
        sys.exit(0)
        
    commit_message = f"docs(VLORs): Automated backup for {timestamp}"
    run_command(['git', 'commit', '-m', commit_message], cwd=REPO_PATH)
    
    repo_url = f"https://{github_token}@github.com/IsidoreLands/Isidore-Operations-MCT.git"
    run_command(['git', 'push', repo_url, branch_name], cwd=REPO_PATH)
    
    pr_title = f"Automated VLOR Backup: {timestamp}"
    pr_body = "Automated periodic backup of VLOR pages from the wiki. Please review and merge."
    auth_env = os.environ.copy()
    auth_env['GH_TOKEN'] = github_token
    run_command(['gh', 'pr', 'create', '--title', pr_title, '--body', pr_body, '--base', 'main', '--head', branch_name], cwd=REPO_PATH, env=auth_env)
    
    run_command(['git', 'checkout', 'main'], cwd=REPO_PATH)
    run_command(['git', 'branch', '-D', branch_name], cwd=REPO_PATH)

    print("\n--- Category-Based VLOR Backup Protocol Complete ---")

if __name__ == '__main__':
    main()
