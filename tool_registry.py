# tool_registry.py
# Version 1.2
# Corrected input string parsing for tool functions.

from langchain.tools import Tool
import page_tool

def get_approved_tools():
    """
    Initializes and returns a curated list of approved tools for the agent.
    """
    print("--- Initializing approved tools from registry ---")

    site = page_tool.get_wiki_site()

    approved_tool_list = [
        Tool(
            name="find_and_replace_on_wiki_page",
            # CORRECTED: Use rsplit to handle complex strings.
            func=lambda input_str: page_tool.find_and_replace(
                site,
                input_str.rsplit(',', 2)[2].strip().strip("'\""), # title_str
                input_str.rsplit(',', 2)[0].strip().strip("'\""), # find_str
                input_str.rsplit(',', 2)[1].strip().strip("'\""), # replace_str
                "AIOps Agent: find_and_replace",
                0 # count=0 for all instances
            ),
            description="Use this to surgically find and replace a specific string on a given wiki page. Input must be a comma-separated list of three strings in this order: string_to_find, string_to_replace_with, page_title."
        ),
        Tool(
            name="append_text_to_wiki_page",
            # CORRECTED: Use rsplit for robust parsing.
            func=lambda input_str: page_tool.append_to_page(
                site,
                input_str.rsplit(',', 1)[1].strip().strip("'\""), # title_str
                input_str.rsplit(',', 1)[0].strip().strip("'\""), # content_str
                "AIOps Agent: append_to_page"
            ),
            description="Use this to append a block of text to the very end of a given wiki page. Input must be a comma-separated list of two strings in this order: content_to_append, page_title."
        ),
    ]

    return approved_tool_list

# For testing purposes
if __name__ == '__main__':
    tools = get_approved_tools()
    print(f"Registry contains {len(tools)} approved tools:")
    for tool in tools:
        print(f"- {tool.name}")
