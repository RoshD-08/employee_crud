import re

def update_file():
    with open('templates/index.html', 'r') as f:
        content = f.read()

    # Wrap Edit and Delete in a role check
    pattern = r'(<a href="\{\{ url_for\(\'edit_employee\'.*?</a>\s*<form method="POST" action="\{\{ url_for\(\'delete_employee\'.*?</form>)'
    replacement = r'{% if g.user and g.user.role in ["Admin", "HR"] %}\n                  \1\n                  {% endif %}'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Wrap + New employee in a role check at the bottom
    pattern2 = r'(\{%\s*if not search and not selected_department and not selected_status\s*%\}\s*<a href="\{\{ url_for\(\'add_employee\'\)\}\}".*?</a>\s*\{%\s*endif\s*%\})'
    replacement2 = r'{% if g.user and g.user.role in ["Admin", "HR"] %}\n      \1\n      {% endif %}'
    content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

    with open('templates/index.html', 'w') as f:
        f.write(content)

update_file()
