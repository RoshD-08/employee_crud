import re

with open('templates/view_employee.html', 'r') as f:
    content = f.read()

pattern = r'<div>\s*<p class="text-xs font-semibold uppercase tracking-wide text-ink/50 mb-1">ESI Number</p>\s*<p class="text-sm text-ink">\{\{ employee\.esi_number or \'—\' \}\}</p>\s*</div>'

content = re.sub(pattern, '', content, flags=re.DOTALL)

with open('templates/view_employee.html', 'w') as f:
    f.write(content)

