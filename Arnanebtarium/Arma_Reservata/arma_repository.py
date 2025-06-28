#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arma Script: repository
Version: 1.0.0.L
Role: Directly creates or updates a file in a GitHub repository.
      This is a powerful tool and should be handled with care by orchestrators.
"""
import sys
import json
import os
from github import Github, GithubException
from dotenv import load_dotenv

def main():
    try:
        command = json.load(sys.stdin)
        params = command['parameters']
        repo_path = params['repo_path']
        content = params['content']
        commit_message = params['commit_message']
    except (json.JSONDecodeError, KeyError) as e:
        report_failure(f"Invalid command structure: {e}")
        return

    try:
        load_dotenv(dotenv_path=os.path.expanduser("~/aiops_toolkit/.env"))
        github_pat = os.getenv("GITHUB_PAT")
        repo_name = "IsidoreLands/AIOps-Toolkit"

        if not github_pat:
            raise ValueError("GITHUB_PAT not found in .env file.")

        g = Github(github_pat)
        repo = g.get_repo(repo_name)

        try:
            # Check if the file already exists to decide between update and create
            existing_file = repo.get_contents(repo_path)
            # If it exists, update it
            result = repo.update_file(
                path=repo_path,
                message=commit_message,
                content=content,
                sha=existing_file.sha
            )
        except GithubException as e:
            if e.status == 404:
                # If it doesn't exist, create it
                result = repo.create_file(
                    path=repo_path,
                    message=commit_message,
                    content=content
                )
            else:
                # Re-raise other GitHub errors
                raise e
        
        report_success({
            "repo_path": repo_path,
            "commit_sha": result['commit'].sha,
            "commit_url": result['commit'].html_url
        })

    except Exception as e:
        report_failure(f"{type(e).__name__}: {e}")

def report_failure(error_message):
    print(json.dumps({"status": "failure", "action": "repository_push", "error_message": str(error_message)}, indent=2))
    sys.exit(1)

def report_success(result_data):
    print(json.dumps({"status": "success", "action": "repository_push", "result": result_data}, indent=2))

if __name__ == '__main__':
    main()
