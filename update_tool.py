# update_tool.py
# Version 1.0
# A tool to securely fetch the latest version of a script from the project's GitHub repo.

import os
import sys
import argparse
from github import Github, GithubException
from dotenv import load_dotenv

def update_tool_from_github(file_path):
    """
    Fetches a file from the GitHub repository and overwrites the local version.

    Args:
        file_path (str): The relative path of the file within the repository (e.g., 'page_tool.py').
    """
    try:
        # Load environment variables from the .env file
        load_dotenv()
        github_pat = os.getenv("GITHUB_PAT")
        repo_name = "IsidoreLands/AIOps-Toolkit" # The full name of the repository

        if not github_pat:
            print("Error: GITHUB_PAT not found. Please check your .env file.")
            return

        print(f"Connecting to GitHub repository '{repo_name}'...")
        # Authenticate with the GitHub API using the Personal Access Token
        g = Github(github_pat)
        repo = g.get_repo(repo_name)

        print(f"Fetching latest version of '{file_path}'...")
        # Get the contents of the specified file from the repo
        remote_file = repo.get_contents(file_path)
        
        # The content is base64 encoded, so we must decode it
        decoded_content = remote_file.decoded_content.decode('utf-8')

        print(f"Writing updated content to local file '{file_path}'...")
        # Write the decoded content to the local file, overwriting it
        with open(file_path, 'w', encoding='utf-8') as local_file:
            local_file.write(decoded_content)
        
        print(f"\nSuccess: '{file_path}' has been updated to the latest version from GitHub.")

    except GithubException as e:
        if e.status == 404:
            print(f"Error: File '{file_path}' not found in the repository '{repo_name}'.")
        else:
            print(f"A GitHub API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Update a local tool script from the project's GitHub repository.")
    parser.add_argument('filename', help="The name of the file to update (e.g., 'page_tool.py').")
    args = parser.parse_args()

    update_tool_from_github(args.filename)
