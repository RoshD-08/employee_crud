import re

with open('templates/view_employee.html', 'r') as f:
    content = f.read()

content = content.replace(
    "        <p class=\"text-sm text-white/70 mt-1\">{{ employee.position or '—' }} &middot; {{ employee.department or '—' }}</p>\n      </div>",
    "        <p class=\"text-sm text-white/70 mt-1\">{{ employee.position or '—' }} &middot; {{ employee.department or '—' }}</p>\n        </div>\n      </div>"
)

with open('templates/view_employee.html', 'w') as f:
    f.write(content)
