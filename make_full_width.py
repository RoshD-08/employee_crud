import os
import re

def update_file(filepath, pattern, replacement):
    with open(filepath, 'r') as f:
        content = f.read()
    content = re.sub(pattern, replacement, content)
    with open(filepath, 'w') as f:
        f.write(content)

# Update base.html
base_path = 'templates/base.html'
with open(base_path, 'r') as f:
    content = f.read()
content = content.replace('max-w-6xl mx-auto px-6', 'w-full px-4 sm:px-6 lg:px-8')
with open(base_path, 'w') as f:
    f.write(content)

# Update other templates to replace max-w-[a-z0-9]+ mx-auto with w-full
templates_dir = 'templates/'
for filename in os.listdir(templates_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(templates_dir, filename)
        if filename != 'base.html' and filename != 'login.html':
            with open(filepath, 'r') as f:
                content = f.read()
            # Replace common layout wrappers
            content = re.sub(r'max-w-[a-z0-9]+\s+mx-auto', 'w-full', content)
            with open(filepath, 'w') as f:
                f.write(content)
