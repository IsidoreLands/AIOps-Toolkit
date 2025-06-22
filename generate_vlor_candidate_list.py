#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# AIOps Toolkit: VLOR Candidate Lister
# Version: 3.2.0 (Space-Aware Discovery)
#
# This script robustly discovers VLORs and related pages by scanning only
# within the OODA_WIKI namespace and correctly handling spaces in titles.

import pywikibot
from datetime import datetime

# --- CONFIGURATION ---
TARGET_NAMESPACE = "OODA_WIKI"
# Use spaces as returned by the API
CONFIDENT_PREFIX = 'OODA WIKI:WikiProject ' 
CONFIDENT_SUFFIX = '/VLOR'
# Use spaces in keywords for accurate matching
UNCERTAIN_KEYWORDS = ['VLOR', 'Virtuous Loop', 'Roadmap'] 
OUTPUT_FILENAME = 'vlor_candidate_report.txt'

def main():
    """
    Main execution function. Connects to the wiki and generates a list of
    pages with VLOR in their titles, sorted into categories.
    """
    print("--- Starting VLOR Candidate Discovery Protocol ---")
    site = pywikibot.Site()
    site.login()

    try:
        # Get the namespace object from its name
        ns = site.namespaces[TARGET_NAMESPACE]
    except KeyError:
        print(f"FATAL ERROR: Namespace '{TARGET_NAMESPACE}' not found on this wiki.")
        return

    print(f"\nDiscovering all pages in the '{TARGET_NAMESPACE}' namespace...")
    all_pages_generator = site.allpages(namespace=ns.id)
    
    confident_vlors = []
    uncertain_vlors = []
    error_logs = []
    
    # This loop should now be safe from cross-namespace errors
    while True:
        try:
            page = next(all_pages_generator)
            page_title = page.title()
            
            # Normalize the title to use spaces for consistent matching
            normalized_title = page_title.replace('_', ' ')

            # Classify the page based on its title
            if normalized_title.startswith(CONFIDENT_PREFIX) and normalized_title.endswith(CONFIDENT_SUFFIX):
                confident_vlors.append(page_title)
            # A page is 'uncertain' if it contains any other keyword
            elif any(keyword in normalized_title for keyword in UNCERTAIN_KEYWORDS):
                uncertain_vlors.append(page_title)

        except StopIteration:
            print("Finished iterating through all namespace pages.")
            break
        except Exception as e:
            # Catch any other unexpected errors during discovery
            error_message = f"Unexpected error during page discovery: {e}"
            print(f"  - WARNING: {error_message}")
            error_logs.append(error_message)
            continue
            
    # --- Generate the report file ---
    print(f"\nWriting results to '{OUTPUT_FILENAME}'...")
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        f.write(f"VLOR Candidate Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write(f"Scope: Namespace '{TARGET_NAMESPACE}'\n")
        f.write("="*40 + "\n\n")

        # Section 1: Confident VLORs
        f.write(f"Confident VLORs ({len(confident_vlors)})\n")
        f.write(f"Pages matching the '{CONFIDENT_PREFIX}...{CONFIDENT_SUFFIX}' pattern.\n")
        f.write("-"*40 + "\n")
        if confident_vlors:
            confident_vlors.sort()
            for title in confident_vlors:
                f.write(f"{title}\n")
        else:
            f.write("None found.\n")
        f.write("\n\n")

        # Section 2: Uncertain VLORs
        f.write(f"Uncertain VLORs ({len(uncertain_vlors)})\n")
        f.write(f"Pages containing one of {UNCERTAIN_KEYWORDS} but not matching the confident pattern.\n")
        f.write("-"*40 + "\n")
        if uncertain_vlors:
            uncertain_vlors.sort()
            for title in uncertain_vlors:
                f.write(f"{title}\n")
        else:
            f.write("None found.\n")
        f.write("\n\n")

        # Section 3: Errors (should now be empty)
        f.write(f"Errors Encountered During Discovery ({len(error_logs)})\n")
        f.write("These logs indicate pages that could not be processed by the API.\n")
        f.write("-"*40 + "\n")
        if error_logs:
            for error in error_logs:
                f.write(f"- {error}\n")
        else:
            f.write("None.\n")

    print("\n--- Discovery Protocol Complete ---")
    print(f"Review the generated report by running: nano {OUTPUT_FILENAME}")

if __name__ == '__main__':
    main()
