#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AIOps Toolkit: Automated VLOR Backup Utility
# Version: 6.0.0 (Dual Repository Push)
#
# This script discovers VLORs, generates a dashboard, backs up raw VLORs
# to a private repo, and pushes the public dashboard to a separate public repo.

import os
import subprocess
import sys
from datetime import datetime
from dotenv import load_dotenv
import pywikibot
import re
import mwparserfromhell

# --- CONFIGURATION ---
PRIVATE_REPO_PATH = os.path.expanduser('~/Isidore-Operations-MCT')
PUBLIC_REPO_PATH = os.path.expanduser('~/Isidore-Operations-Dashboard')
VLOR_FOLDER_NAME = 'VLORs'
DASHBOARD_FILENAME = 'Operations_Dashboard.md'
ENV_FILE_PATH = os.path.expanduser('~/aiops_toolkit/.env.vlor_backup')
DISCOVERY_CATEGORIES = ['Category:Initiative VLOR', 'Category:Operation VLOR']

def get_vlor_pages_from_categories(site):
    """Reads wiki categories to get a list of VLOR pages."""
    all_vlor_pages = []
    page_titles = set()
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
    """Creates a safe filename from a wiki page title."""
    title = title.replace(' ', '_')
    match = re.search(r'WikiProject_([^/]+)/([^/]+)/VLOR', title)
    if match:
        project, operation = match.group(1), match.group(2)
        return f"{project}_{operation}.mw"
    match_initiative = re.search(r'WikiProject_([^/]+)/VLOR', title)
    if match_initiative:
        project = match_initiative.group(1)
        return f"{project}_Initiative.mw"
    return title.replace(':', '_').replace('/', '_') + ".mw"

def run_command(command, cwd, env=None):
    """Executes a shell command and handles errors."""
    print(f"Executing in {cwd}: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd, env=env)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(result.stdout)
    return result

def generate_dashboard(vlor_pages):
    """Parses VLOR pages and generates a Markdown dashboard."""
    # (Content of this function remains the same as version 5.1.0)
    dashboard_content = f"# Operations Dashboard\n_Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}_\n\n"
    dashboard_content += "This document provides a consolidated, high-level overview of all active and planned operational loops.\n\n"
    for page in sorted(vlor_pages, key=lambda p: p.title()):
        wikicode = mwparserfromhell.parse(page.text)
        operation_name = "Unknown"
        for template in wikicode.filter_templates(matches="IsidoreOodaVLOR"):
            if template.has("operation"):
                operation_name = template.get("operation").value.strip()
                break
        dashboard_content += f"## From VLOR: [[{page.title()}]] (Operation: {operation_name})\n\n"
        for template in wikicode.filter_templates(matches="IsidoreOodaVLOR"):
            try:
                loop_id = template.get("loop_id").value.strip()
                human_title = template.get("human_title").value.strip()
                status = template.get("status").value.strip()
                description = template.get("description").value.strip()
                dashboard_content += f"### {human_title} (`{loop_id}`)\n"
                dashboard_content += f"**Status:** {status}\n\n"
                dashboard_content += f"**Description:** {description}\n\n"
                if template.has("resources"):
                    resources = template.get("resources").value.strip()
                    if resources:
                        dashboard_content += f"**Anticipated Resources:** `{resources}`\n\n"
                dashboard_content += "---\n"
            except ValueError:
                continue
    return dashboard_content

def main():
    """Main execution function."""
    print("="*60 + "\nREMINDER: The GitHub PAT has a 90-day expiration.\n" + "="*60)
    
    print(f"--- Starting Dual-Repo VLOR Backup @ {datetime.now()} ---")
    
    load_dotenv(dotenv_path=ENV_FILE_PATH)
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print(f"ERROR: GITHUB_TOKEN not found in {ENV_FILE_PATH}", file=sys.stderr)
        sys.exit(1)

    site = pywikibot.Site()
    site.login()
    vlor_pages = get_vlor_pages_from_categories(site)
    
    # --- Part 1: Generate Content ---
    print("\n--- Generating content from wiki... ---")
    dashboard_text = generate_dashboard(vlor_pages)

    # --- Part 2: Update Private MCT Repository ---
    print("\n--- Processing Private MCT Repository... ---")
    timestamp = datetime.now().strftime('%Y-%m-%d-%H%M')
    branch_name = f"auto-backup/{timestamp}"
    run_command(['git', 'fetch', 'origin'], cwd=PRIVATE_REPO_PATH)
    run_command(['git', 'checkout', 'origin/main', '-b', branch_name], cwd=PRIVATE_REPO_PATH)
    
    # Backup raw VLOR files
    target_dir = os.path.join(PRIVATE_REPO_PATH, VLOR_FOLDER_NAME)
    os.makedirs(target_dir, exist_ok=True)
    for page in vlor_pages:
        file_name = generate_filename_from_title(page.title())
        file_path = os.path.join(target_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f: f.write(page.text)
    
    status_result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=PRIVATE_REPO_PATH)
    if not status_result.stdout.strip():
        print("No changes detected in private repo. Exiting private repo update.")
    else:
        run_command(['git', 'add', f'{VLOR_FOLDER_NAME}/'], cwd=PRIVATE_REPO_PATH)
        commit_message = f"docs(VLORs): Automated backup for {timestamp}"
        run_command(['git', 'commit', '-m', commit_message], cwd=PRIVATE_REPO_PATH)
        repo_url_private = f"https://{github_token}@github.com/IsidoreLands/Isidore-Operations-MCT.git"
        run_command(['git', 'push', repo_url_private, branch_name], cwd=PRIVATE_REPO_PATH)
        pr_title = f"Automated VLOR Backup: {timestamp}"
        pr_body = "Automated periodic backup of VLOR pages from the wiki. Please review and merge."
        auth_env = os.environ.copy(); auth_env['GH_TOKEN'] = github_token
        run_command(['gh', 'pr', 'create', '--title', pr_title, '--body', pr_body, '--base', 'main', '--head', branch_name], cwd=PRIVATE_REPO_PATH, env=auth_env)
        run_command(['git', 'checkout', 'main'], cwd=PRIVATE_REPO_PATH)
        run_command(['git', 'branch', '-D', branch_name], cwd=PRIVATE_REPO_PATH)

    # --- Part 3: Update Public Dashboard Repository ---
    print("\n--- Processing Public Dashboard Repository... ---")
    run_command(['git', 'pull', 'origin', 'main'], cwd=PUBLIC_REPO_PATH)
    dashboard_path = os.path.join(PUBLIC_REPO_PATH, DASHBOARD_FILENAME)
    with open(dashboard_path, 'w', encoding='utf-8') as f: f.write(dashboard_text)
    
    status_result_public = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, cwd=PUBLIC_REPO_PATH)
    if not status_result_public.stdout.strip():
        print("No changes detected in public dashboard. Exiting public repo update.")
    else:
        run_command(['git', 'add', DASHBOARD_FILENAME], cwd=PUBLIC_REPO_PATH)
        commit_message_public = f"docs: Update Operations Dashboard for {timestamp}"
        run_command(['git', 'commit', '-m', commit_message_public], cwd=PUBLIC_REPO_PATH)
        run_command(['git', 'push', 'origin', 'main'], cwd=PUBLIC_REPO_PATH)

    print("\n--- Dual-Repo Backup Protocol Complete ---")

if __name__ == '__main__':
    main()
