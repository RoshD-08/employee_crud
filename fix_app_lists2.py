import re

with open('app.py', 'r') as f:
    content = f.read()

helper_func = """
def get_list_setting(key, default_list):
    val = get_company_setting(key, None)
    if not val:
        return default_list
    return [x.strip() for x in val.split(',') if x.strip()]
"""

content = content.replace(
    '        conn.close()\n\n\n# ── Validation ──',
    '        conn.close()\n' + helper_func + '\n# ── Validation ──'
)

with open('app.py', 'w') as f:
    f.write(content)
