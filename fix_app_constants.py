import re

with open('app.py', 'r') as f:
    content = f.read()

# Remove _form_constants definition
content = re.sub(r'def _form_constants\(\):.*?\}\n\n\n', '\n', content, flags=re.DOTALL)

# Remove usage
content = content.replace(', **_form_constants()', '')

with open('app.py', 'w') as f:
    f.write(content)
