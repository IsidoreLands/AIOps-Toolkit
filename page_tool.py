#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A definitive, general-purpose tool for MediaWiki operations.
Now includes LLM-powered summarization.
Version 18.1.0 (Stable Main Dispatcher)
"""

import sys
import argparse
import pywikibot
import mwparserfromhell
import os
import llm_service # Assuming llm_service.py is in the same directory orPYTHONPATH

# --- Environment Variable Name for Overwrite Confirmation ---
OVERWRITE_APPROVAL_ENV_VAR = "AIOPS_TOOLKIT_OVERWRITE_APPROVAL_TOKEN"
EXPECTED_OVERWRITE_TOKEN = "20 Second Boyd!"

# --- Core Functions ---
def get_wiki_site():
    """Connects to the site using configured credentials and returns a site object."""
    site = pywikibot.Site()
    site.login()
    return site

def get_page_and_wikicode(site, page_title, ensure_exists=True):
    """
    Gets a page object and its parsed wikitext.
    """
    page = pywikibot.Page(site, page_title)
    if ensure_exists and not page.exists():
        print(f"Error: Page '{page_title}' does not exist.")
        sys.exit(1)
    return page, mwparserfromhell.parse(page.text)

# --- Action Functions ---

def write_full_page(site, page_title, new_content, summary):
    """Writes content to a new page. FOR CREATING NEW PAGES ONLY."""
    page = pywikibot.Page(site, page_title)
    if page.exists():
        print(f"CRITICAL ERROR: Page '{page_title}' already exists. Use '--action overwrite' for existing pages (with confirmation).")
        print(f"Halting 'write' action as per safety protocols.")
        sys.exit(1)
    page.text = new_content
    try:
        page.save(summary=summary, bot=True)
        print(f"Success: Page '{page_title}' was created.")
        print(f"Revision URL: {page.permalink()}")
    except pywikibot.exceptions.Error as e:
        print(f"Error saving (create) page '{page_title}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during page creation: {e}")
        sys.exit(1)

def overwrite_page(site, page_title, new_content, summary):
    """Overwrites an existing page with new content. Requires environment variable confirmation."""
    approval_token = os.environ.get(OVERWRITE_APPROVAL_ENV_VAR)
    if approval_token != EXPECTED_OVERWRITE_TOKEN:
        print(f"\n!!! OVERWRITE ACTION HALTED for page '{page_title}' !!!")
        print(f"To proceed, you must first set the environment variable correctly.")
        print(f"  Example: export {OVERWRITE_APPROVAL_ENV_VAR}=\"{EXPECTED_OVERWRITE_TOKEN}\"")
        print(f"Current value of {OVERWRITE_APPROVAL_ENV_VAR}: '{approval_token if approval_token else 'Not Set'}'")
        sys.exit(1)
    page, _ = get_page_and_wikicode(site, page_title, ensure_exists=True)
    print(f"\nProceeding with overwrite for page: '{page_title}' (Approval token accepted).")
    page.text = new_content
    try:
        page.save(summary=summary, bot=True)
        print(f"Success: Page '{page_title}' was overwritten.")
        print(f"Revision URL: {page.permalink()}")
    except pywikibot.exceptions.Error as e:
        print(f"Error saving (overwrite) page '{page_title}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during page overwrite: {e}")
        sys.exit(1)

def find_and_replace(site, page_title, find_text, replace_text, summary, count=1):
    """Finds and replaces occurrences of a specific string on a page."""
    page, _ = get_page_and_wikicode(site, page_title) # Ensure page exists for reading
    original_text = page.text
    if count == 0: # Replace all occurrences if count is 0
        new_text = original_text.replace(find_text, replace_text)
    elif count > 0: # Replace a specific number of occurrences
        new_text = original_text.replace(find_text, replace_text, count)
    else: # Negative count is invalid
        print(f"Error: Invalid replace_count '{count}'. Must be 0 (all) or positive.")
        sys.exit(1)

    if new_text == original_text:
        print(f"Warning: The text '{find_text}' was not found on page '{page_title}' (or replace_text is identical). No edit was made.")
        sys.exit(0) # Not an error, but no change made
    page.text = new_text
    try:
        page.save(summary=summary, bot=True)
        print(f"Success: Replaced text on page '{page_title}'.")
        print(f"Revision URL: {page.permalink()}")
    except pywikibot.exceptions.Error as e:
        print(f"Error saving (find_and_replace) page '{page_title}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during find_and_replace save: {e}")
        sys.exit(1)

def append_to_section(site, page_title, section_title, append_content, summary):
    """Safely appends text to the end of a specific section of a page."""
    page, wikicode = get_page_and_wikicode(site, page_title) # Ensure page exists

    section_found = False
    for section_idx, section in enumerate(wikicode.get_sections(flat=True, include_lead=True)):
        headings = section.filter_headings()
        current_section_title = ""
        if headings:
            current_section_title = headings[0].title.strip()

        # Match lead/intro section (section_title can be '0', 'lead', or 'introduction')
        is_lead_section_match = not headings and section_title.lower() in ['0', 'lead', 'introduction']

        if is_lead_section_match or current_section_title == section_title:
            # Append new content to the found section
            # Ensure there's a newline before appended content if section isn't empty and doesn't end with newline
            current_section_str = str(section).rstrip('\n')
            if current_section_str: # If section has content
                 wikicode.insert(wikicode.index(section) + len(section), f"\n{append_content}")
            else: # Section is empty or just whitespace
                 wikicode.insert(wikicode.index(section) + len(section), append_content)

            section_found = True
            break

    if not section_found:
        print(f"Error: Could not find section titled '{section_title}'. Ensure title matches exactly (case-sensitive) or use '0' for lead section.")
        sys.exit(1)

    page.text = str(wikicode)
    try:
        page.save(summary=summary, bot=True)
        print(f"Success: Content appended to section '{section_title}' on page '{page_title}'.")
        print(f"Revision URL: {page.permalink()}")
    except pywikibot.exceptions.Error as e:
        print(f"Error saving (append_to_section) page '{page_title}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during append_to_section save: {e}")
        sys.exit(1)

def write_template_field(site, page_title, template_name, target_id_param_name, target_id_value, field_to_edit, new_field_value, summary):
    """Writes a value to a specific field in a targeted template on a page."""
    page, wikicode = get_page_and_wikicode(site, page_title) # Ensure page exists
    template_found_and_edited = False
    for template in wikicode.filter_templates():
        if template.name.matches(template_name):
            if template.has(target_id_param_name) and template.get(target_id_param_name).value.strip() == target_id_value:
                if template.has(field_to_edit):
                    template.get(field_to_edit).value = f" {new_field_value} " # Add spaces for cleaner formatting
                else:
                    template.add(field_to_edit, f" {new_field_value} ", before=None) # Add new param if not exist
                template_found_and_edited = True
                break # Assuming only one such template instance needs editing

    if not template_found_and_edited:
        print(f"Error: Template '{template_name}' with '{target_id_param_name}={target_id_value}' and field '{field_to_edit}' not found or field not editable as expected.")
        sys.exit(1)

    page.text = str(wikicode)
    try:
        page.save(summary=summary, bot=True)
        print(f"Success: Field '{field_to_edit}' in template '{template_name}' (ID: {target_id_value}) updated on page '{page_title}'.")
        print(f"Revision URL: {page.permalink()}")
    except pywikibot.exceptions.Error as e:
        print(f"Error saving (write_template_field) page '{page_title}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during write_template_field save: {e}")
        sys.exit(1)


def summarize_section(site, page_title, section_title):
    """Gets section text and uses an LLM to summarize it."""
    page, wikicode = get_page_and_wikicode(site, page_title) # Ensure page exists

    section_text_found = ""
    for section in wikicode.get_sections(include_lead=True, flat=True):
        headings = section.filter_headings()
        current_section_title_from_heading = ""
        if headings:
            current_section_title_from_heading = headings[0].title.strip()

        is_lead_section_match = not headings and section_title.lower() in ['0', 'lead', 'introduction']

        if is_lead_section_match or current_section_title_from_heading == section_title:
            section_text_found = section.strip_code().strip() # Get clean text
            break

    if not section_text_found:
        print(f"Error: Could not find section titled '{section_title}' for summarization.")
        sys.exit(1)

    print(f"Content fetched from section '{section_title}'. Sending to LLM for summarization...")
    # Ensure llm_service.py and its functions (e.g., call_gemini) are correctly implemented and imported
    prompt = f"Please provide a concise, one-paragraph summary of the following text:\n\n---\n{section_text_found}\n---"
    llm_summary = llm_service.call_gemini(prompt) # Changed variable name to avoid conflict

    print("\n--- Summary from Model ---")
    print(llm_summary)
    print("--------------------------")

def append_to_page(site, page_title, append_content, summary):
    """Appends content to the very end of a page."""
    page, _ = get_page_and_wikicode(site, page_title) # Ensure page exists
    
    # Ensure there's a newline before the new content
    if not page.text.endswith('\n'):
        page.text += '\n'
        
    page.text += append_content
    
    try:
        page.save(summary=summary, bot=True)
        print(f"Success: Content appended to page '{page_title}'.")
        print(f"Revision URL: {page.permalink()}")
    except pywikibot.exceptions.Error as e:
        print(f"Error saving (append_to_page) page '{page_title}': {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during append_to_page save: {e}")
        sys.exit(1)

# --- Main Dispatcher ---
def main():
    parser = argparse.ArgumentParser(
        description='A unified tool for MediaWiki editing, now with LLM summarization. Version 18.1.0 (Stable Main Dispatcher)',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--action',
                        choices=['write', 'overwrite', 'append_to_section', 'find_and_replace', 'write_field', 'summarize_section'],
                        required=True,
                        help="The action to perform.")
    # ... (all other argparse arguments as they were, they are correct) ...
    parser.add_argument('--title', required=True, help="The title of the MediaWiki page.")
    parser.add_argument('--content', help="Direct string content for write/overwrite/append actions.")
    parser.add_argument('--from-file', help="Path to a file containing content for write/overwrite/append actions.")
    parser.add_argument('--section-title', help="The title of the section for 'append_to_section' or 'summarize_section'. Use '0' or 'lead' for the lead section.")
    parser.add_argument('--find', help="String to find for 'find_and_replace'.")
    parser.add_argument('--replace', help="String to replace with for 'find_and_replace'. Can be empty.")
    parser.add_argument('--replace-count', type=int, default=1, help="Occurrences to replace for 'find_and_replace'. Use 0 for all. Default is 1.")
    parser.add_argument('--template-name', help="Name of the template for 'write_field' (e.g., 'IsidoreOodaVLOR').")
    parser.add_argument('--target-id-param', default='loop_id', help="Template parameter name holding the unique identifier (e.g., 'loop_id', 'uid'). Default: 'loop_id'. For 'write_field'.")
    parser.add_argument('--target-id-value', help="Unique ID value of the template instance to target (e.g., 'ALCUIN-L001'). For 'write_field'.")
    parser.add_argument('--field', help="Template field name (parameter name) to write to. For 'write_field'.")
    parser.add_argument('--value', help="New value for the template field. Can be empty. For 'write_field'.")

    args = parser.parse_args()

    try:
        site = get_wiki_site()
    except Exception as e:
        print(f"Failed to connect to wiki or login: {e}")
        sys.exit(1)

    # Determine content source for actions that need it
    content_for_actions = ""
    if args.action in ['write', 'overwrite', 'append_to_section']:
        if args.content:
            content_for_actions = args.content
        elif args.from_file:
            try:
                with open(args.from_file, 'r', encoding='utf-8') as f:
                    content_for_actions = f.read()
            except FileNotFoundError:
                parser.error(f"--from-file: File not found at '{args.from_file}'")
            except Exception as e:
                parser.error(f"--from-file: Error reading file '{args.from_file}': {e}")
        # For 'append_to_section', if neither --content nor --from-file is given for text to append, it might be an issue.
        # However, some might want to append effectively nothing if that's the only way to trigger other logic,
        # but typically content is expected for append. The functions will handle if content_for_actions is empty.

    # Default summary, can be more specific per action if needed
    summary_action_verb = args.action.replace('_', ' ')
    summary = f"AIOps Toolkit (v18.1.0): {summary_action_verb} on page '{args.title}'"
    if args.action == 'summarize_section': # summarize_section doesn't make an edit, so summary is less relevant unless logged
        summary = f"AIOps Toolkit (v18.1.0): analyzed section '{args.section_title}' on page '{args.title}' for summarization"

    # Dispatch to appropriate action function
    if args.action == 'write':
        if not content_for_actions: # write requires content
            parser.error("Action 'write' requires --content or --from-file.")
        write_full_page(site, args.title, content_for_actions, summary)
    elif args.action == 'overwrite':
        if not content_for_actions: # overwrite requires content
            parser.error("Action 'overwrite' requires --content or --from-file.")
        overwrite_page(site, args.title, content_for_actions, summary)
    elif args.action == 'append_to_section':
        if not args.section_title:
            parser.error("Action 'append_to_section' requires --section-title.")
        # content_for_actions will be the text to append (can be empty if desired, though usually not)
        append_to_section(site, args.title, args.section_title, content_for_actions, summary)
    elif args.action == 'find_and_replace':
        if args.find is None or args.replace is None: # find is required, replace can be empty
            parser.error("Action 'find_and_replace' requires --find and --replace arguments.")
        find_and_replace(site, args.title, args.find, args.replace, summary, args.replace_count)
    elif args.action == 'write_field':
        if not all([args.template_name, args.target_id_value, args.field]): # value can be empty
             parser.error("Action 'write_field' requires --template-name, --target-id-value, and --field. --value can be empty but must be provided if not an empty string.")
        # Ensure args.value is provided, even if it's an empty string. If not provided at all, it's None.
        value_to_write = args.value if args.value is not None else ""
        write_template_field(site, args.title, args.template_name, args.target_id_param, args.target_id_value, args.field, value_to_write, summary)
    elif args.action == 'summarize_section':
        if not args.section_title:
            parser.error("Action 'summarize_section' requires --section-title.")
        summarize_section(site, args.title, args.section_title) # This action prints, doesn't save to wiki with 'summary'
    else:
        # This should not be reached due to 'choices' in argparse
        print(f"Internal Error: Unhandled action '{args.action}'.")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except pywikibot.exceptions.NoUsernameError:
        print("Pywikibot Error: No username configured. Please run 'pwb.py login'.")
        sys.exit(1)
    except Exception as e:
        print(f"An unhandled error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
