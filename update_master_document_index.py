import pywikibot
import mwparserfromhell

site = pywikibot.Site()
vlor_map = {}
for cat in ['Initiative_VLOR', 'Operation_VLOR']:
    category = pywikibot.Category(site, f'Category:{cat}')
    for page in category.articles():
        wikicode = mwparserfromhell.parse(page.text)  # Correct parsing
        for t in wikicode.filter_templates(matches='IsidoreOodaVLOR'):
            if t.has('operation'):
                vlor_map[t.get('operation').value.strip().upper()] = page.title()

page = pywikibot.Page(site, 'OODA_WIKI:WikiProject_Isidore/Alcuin/Master_Document_Index')
page.text = '; VLORs:\n' + '\n'.join(f'* [[{title}]] - {op} roadmap' for op, title in vlor_map.items()) + '\n; RMR:\n* [[OODA_WIKI:WikiProject_Isidore/RMR]] - Rules and Metarules'
page.save(summary='Updated Master Document Index with dynamic VLORs', bot=True)
