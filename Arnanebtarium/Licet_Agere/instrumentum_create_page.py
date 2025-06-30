#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instrumentum Script: create_page
Version: 1.0.0.L
Role: Creates a new wiki page. Fails if the page already exists.
      This is a safe, non-destructive tool.
"""
import sys
import json
import pywikibot

def main():
    try:
        command = json.load(sys.stdin)
        params = command['parameters']
        page_title = params['page_title']
        content = params['content']
        summary = params['summary']
    except (json.JSONDecodeError, KeyError) as e:
        report_failure(f"Invalid command structure: {e}")
        return

    try:
        site = pywikibot.Site()
        site.login()
        page = pywikibot.Page(site, page_title)

        if page.exists():
            raise FileExistsError(f"Page '{page_title}' already exists. This tool is for creation only.")

        page.text = content
        page.save(summary=summary, bot=True)

        report_success({
            "page_title": page_title,
            "revision_url": page.permalink()
        })

    except Exception as e:
        report_failure(f"{type(e).__name__}: {e}")

def report_failure(error_message):
    print(json.dumps({"status": "failure", "action": "create_page", "error_message": str(error_message)}, indent=2))
    sys.exit(1)

def report_success(result_data):
    print(json.dumps({"status": "success", "action": "create_page", "result": result_data}, indent=2))

if __name__ == '__main__':
    main()
