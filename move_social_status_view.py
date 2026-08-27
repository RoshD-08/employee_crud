import re

with open('templates/view_employee.html', 'r') as f:
    content = f.read()

pattern_extract = r'\s*<div>\s*<p class="text-xs font-semibold uppercase tracking-wide text-ink/50 mb-1">Tax Filing Status</p>\s*<p class="text-sm text-ink">\{\{ employee\.tax_filing_status or \'—\' \}\}</p>\s*</div>'

match = re.search(pattern_extract, content, flags=re.DOTALL)
if match:
    block = match.group(0)
    # Remove from original location
    content = content.replace(block, '')
    
    # Update label
    block = block.replace('>Tax Filing Status<', '>Social Status<')
    
    # Insert after Gender block
    gender_block = r'(<div>\s*<p class="text-xs font-semibold uppercase tracking-wide text-ink/50 mb-1">Gender</p>\s*<p class="text-sm text-ink">\{\{ employee\.gender or \'—\' \}\}</p>\s*</div>)'
    
    content = re.sub(gender_block, r'\1' + block, content, flags=re.DOTALL)
else:
    print("Could not find tax_filing_status block in view_employee.html")

with open('templates/view_employee.html', 'w') as f:
    f.write(content)

