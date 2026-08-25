import re

def update_file():
    with open('templates/view_employee.html', 'r') as f:
        content = f.read()

    pattern = r'(<a href="\{\{ url_for\(\'edit_employee\', employee_id=employee\.id\) \}\}".*?</a>\s*<form method="POST" action="\{\{ url_for\(\'delete_employee\'.*?</form>)'
    replacement = r'{% if g.user and g.user.role in ["Admin", "HR"] %}\n        \1\n        {% endif %}'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open('templates/view_employee.html', 'w') as f:
        f.write(content)

update_file()
