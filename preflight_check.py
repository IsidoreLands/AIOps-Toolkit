import pywikibot
import mwparserfromhell
import datetime
import re
import sys

def get_dynamic_vlor_map(site):
    """Dynamically builds VLOR_PAGE_MAP from category pages using template data."""
    vlor_map = {}
    for category_name in ["Initiative_VLOR", "Operation_VLOR"]:
        category = pywikibot.Category(site, f"Category:{category_name}")
        pages = list(category.articles())
        print(f"  - Found {len(pages)} pages in '{category_name}'.")
        for page in pages:
            title = page.title()
            wikicode = mwparserfromhell.parse(page.text)
            for t in wikicode.filter_templates(matches="IsidoreOodaVLOR"):
                if t.has("operation"):
                    operation = t.get("operation").value.strip().upper()
                    vlor_map[operation] = title
                    print(f"  - Mapped: {operation} -> {title}")
    print(f"Total unique VLOR pages mapped: {len(vlor_map)}.")
    return vlor_map

def preflight_check():
    if len(sys.argv) > 1 and sys.argv[1] != __file__:  # Avoid running if imported
        return
    
    site = pywikibot.Site()
    site.login()
    print(f"Logged in as: {site.user()}")  # Debug login
    
    date_str = input("Enter date (YYYY-MM-DD): ").strip()
    if date_str.lower() == "today":
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print("Error: Invalid date format. Use YYYY-MM-DD or 'today'.")
        return
    
    session_name = input("Enter session (Morning/Noon/Afternoon/Evening/Night): ").capitalize()
    if session_name not in ["Morning", "Noon", "Afternoon", "Evening", "Night"]:
        print("Error: Invalid session name.")
        return
    
    loop_id = input("Enter loop ID (e.g., ORCHARD-L001): ").upper()
    if not re.match(r'^[A-Z]+-L\d+$', loop_id):
        print("Error: Invalid loop ID format. Use OPERATION-LNNN.")
        return
    
    ologo_page_title = f"WikiProject_Isidore/OLOGO/{date_str}/{session_name}"
    ologo_page = pywikibot.Page(site, f"OODA_WIKI:{ologo_page_title}")
    print(f"Attempting to save to: {ologo_page.title()}")  # Debug page title
    
    if ologo_page.exists():
        if input("OLOGO page exists. Overwrite? (y/N): ").lower() != 'y':
            print("Aborted.")
            return
    
    vlor_page_title = get_dynamic_vlor_map(site).get(re.match(r'^([A-Z]+)', loop_id).group(1))
    if not vlor_page_title:
        print(f"Error: Operation for '{loop_id}' not found in dynamic VLOR map.")
        return
    
    vlor_page = pywikibot.Page(site, vlor_page_title)
    if not vlor_page.exists():
        print(f"Error: VLOR page '{vlor_page_title}' does not exist.")
        return
        
    wikicode = mwparserfromhell.parse(vlor_page.text)
    loop_content = None
    for template in wikicode.filter_templates():
        if (template.name.strip() == "IsidoreOodaVLOR" and 
            template.has("loop_id") and 
            template.get("loop_id").value.strip().upper() == loop_id):
            loop_content = str(template)
            break
    
    if not loop_content:
        print(f"Error: Loop '{loop_id}' not found in '{vlor_page_title}'.")
        return
    
    vlor_url = f"https://www.ooda.wiki/wiki/{vlor_page_title.replace(' ', '_')}"
    page_content = f"== Session Context: {loop_id} ==\n"
    page_content += f"'''Date:''' {date_str}\n"
    page_content += f"'''Session:''' {session_name}\n"
    page_content += f"'''Loop ID:''' {loop_id}\n"
    page_content += f"'''Source VLOR:''' [[{vlor_page_title}]] ([{vlor_url} link])\n\n"
    page_content += f"<pre>\n{loop_content}\n</pre>\n\n"
    page_content += "== Log Summary ==\n(To be updated post-completion with tools built, challenges, changes, and costs)\n"
    
    ologo_page.text = page_content
    try:
        ologo_page.save(summary=f"Pre-flight Check: Created OLOGO page for {loop_id}", bot=True)
        print(f"Page [[{ologo_page_title}]] saved successfully. Content: {page_content[:50]}...")  # Debug content
    except pywikibot.exceptions.Error as e:
        print(f"Save failed: {e}")
    print(f"URL: https://www.ooda.wiki/wiki/OODA_WIKI:{ologo_page_title.replace(' ', '_')}")

if __name__ == "__main__":
    preflight_check()
