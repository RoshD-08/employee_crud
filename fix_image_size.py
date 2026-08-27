import re

with open('templates/view_employee.html', 'r') as f:
    content = f.read()

# Replace photo img tag
content = content.replace(
    'class="w-20 h-20 rounded-full object-cover border-2 border-white/20"',
    'class="w-32 h-32 rounded-full object-cover border-4 border-white/20 shadow-md"'
)

# Replace placeholder div
content = content.replace(
    'class="w-20 h-20 rounded-full bg-white/10 border-2 border-white/20 flex items-center justify-center"',
    'class="w-32 h-32 rounded-full bg-white/10 border-4 border-white/20 flex items-center justify-center shadow-md"'
)

# Replace svg size
content = content.replace(
    'class="w-10 h-10 text-white/50"',
    'class="w-16 h-16 text-white/50"'
)

with open('templates/view_employee.html', 'w') as f:
    f.write(content)

