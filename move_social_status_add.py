import re

with open('templates/add_employee.html', 'r') as f:
    content = f.read()

# 1. Extract and remove the tax filing status block
pattern_extract = r'\s*<div>\s*<label class="block text-sm font-semibold text-ink mb-1\.5" for="tax_filing_status">Tax Filing Status</label>\s*<select id="tax_filing_status" name="tax_filing_status"[^>]*>.*?<\/select>\s*<\/div>'

match = re.search(pattern_extract, content, flags=re.DOTALL)
if match:
    block = match.group(0)
    # Remove from original location
    content = content.replace(block, '')
    
    # Update label
    block = block.replace('>Tax Filing Status<', '>Social Status<')
    
    # Insert after Gender block
    gender_block = r'(<label class="block text-sm font-semibold text-ink mb-1\.5" for="gender">Gender</label>\s*<select id="gender" name="gender"[^>]*>.*?<\/select>\s*<\/div>)'
    
    content = re.sub(gender_block, r'\1' + block, content, flags=re.DOTALL)
else:
    print("Could not find tax_filing_status block in add_employee.html")

with open('templates/add_employee.html', 'w') as f:
    f.write(content)

