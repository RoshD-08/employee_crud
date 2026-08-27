import re

with open('templates/settings.html', 'r') as f:
    content = f.read()

def block(id, label, var):
    return f"""
                <details class="bg-paper/50 rounded-lg border border-line group">
                    <summary class="cursor-pointer font-semibold text-ink px-4 py-3 flex justify-between items-center select-none outline-none">
                        {label}
                        <span class="transition-transform duration-200 group-open:rotate-180">
                            <svg class="w-5 h-5 text-ink/50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                        </span>
                    </summary>
                    <div class="px-4 pb-4 border-t border-line/50 mt-1 pt-4">
                        <input type="hidden" id="hidden_{id}" name="{id}" value="{{{{ ', '.join({var}) }}}}">
                        
                        <ul id="ul_{id}" class="space-y-2 mb-3"></ul>
                        
                        <div class="flex gap-2">
                            <input type="text" id="add_{id}" class="flex-1 rounded-md border border-line px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent bg-white" placeholder="Type new item..." onkeydown="if(event.key === 'Enter') {{ event.preventDefault(); addItem('{id}'); }}">
                            <button type="button" onclick="addItem('{id}')" class="bg-accent hover:bg-accent-dark text-white text-sm font-semibold px-4 py-1.5 rounded-md transition-colors shadow-sm">Add</button>
                        </div>
                    </div>
                </details>
"""

new_block = f"""<h2 class="text-lg font-bold text-[#14181F] mb-4 border-b border-[#E2E5EA] pb-2">Dropdown Lists & Categories</h2>
            
            <div class="space-y-3 mb-8">
{block('departments', 'Departments', 'departments')}
{block('employment_types', 'Employment Types', 'employment_types')}
{block('employment_statuses', 'Employment Statuses', 'employment_statuses')}
{block('social_statuses', 'Social Statuses', 'tax_filing_statuses')}
{block('genders', 'Genders', 'genders')}
            </div>

            <h2 class="text-lg font-bold text-[#14181F] mb-4 border-b border-[#E2E5EA] pb-2">Bonus & Incentives</h2>"""

pattern = r'<h2 class="text-lg font-bold text-\[\#14181F\] mb-4 border-b border-\[\#E2E5EA\] pb-2">Dropdown Lists & Categories</h2>.*?<h2 class="text-lg font-bold text-\[\#14181F\] mb-4 border-b border-\[\#E2E5EA\] pb-2">Bonus & Incentives</h2>'

content = re.sub(pattern, new_block, content, flags=re.DOTALL)

# Add custom css for details marker removal in safari/firefox if not already there
css_hack = """
  <style>
    /* Subtle stamped-grid texture behind the header — a quiet nod to a paper roster/ledger */
    .roster-texture {
      background-image:
        linear-gradient(to right, #ffffff10 1px, transparent 1px),
        linear-gradient(to bottom, #ffffff10 1px, transparent 1px);
      background-size: 22px 22px;
    }

    /* Dark Mode Filter Hack */
    html.dark-theme {
      filter: invert(1) hue-rotate(180deg);
      background-color: #080705; /* inverted paper */
    }
    
    html.dark-theme img,
    html.dark-theme .leaflet-container {
      filter: invert(1) hue-rotate(180deg);
    }
    
    details > summary {
      list-style: none;
    }
    details > summary::-webkit-details-marker {
      display: none;
    }
  </style>
"""

content = re.sub(r'<style>.*?</style>', css_hack, content, flags=re.DOTALL)

with open('templates/settings.html', 'w') as f:
    f.write(content)

# We also need to add the CSS hack to base.html so the details summary marker is hidden across the app just in case
with open('templates/base.html', 'r') as f:
    base_content = f.read()

if 'details > summary' not in base_content:
    base_content = re.sub(r'<style>.*?</style>', css_hack, base_content, flags=re.DOTALL)
    with open('templates/base.html', 'w') as f:
        f.write(base_content)

