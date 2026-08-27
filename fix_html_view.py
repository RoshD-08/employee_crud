import re

with open('templates/view_employee.html', 'r') as f:
    content = f.read()

# Replace header part
new_header = """
    <!-- Header -->
    <div class="roster-texture bg-ink text-white px-6 py-6 flex items-start justify-between gap-4">
      <div class="flex items-center gap-6">
        {% if employee.photo %}
        <img src="{{ url_for('static', filename='uploads/photos/' ~ employee.photo) }}" alt="Photo" class="w-20 h-20 rounded-full object-cover border-2 border-white/20">
        {% else %}
        <div class="w-20 h-20 rounded-full bg-white/10 border-2 border-white/20 flex items-center justify-center">
            <svg class="w-10 h-10 text-white/50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
        </div>
        {% endif %}
        <div>
          <span class="font-mono text-xs tracking-widest border border-white/30 rounded px-2 py-1 text-accent-light/90">
            EMP-{{ "%04d"|format(employee.id) }}
          </span>
"""

content = content.replace(
    '    <!-- Header -->\n    <div class="roster-texture bg-ink text-white px-6 py-6 flex items-start justify-between gap-4">\n      <div>\n        <span class="font-mono text-xs tracking-widest border border-white/30 rounded px-2 py-1 text-accent-light/90">\n          EMP-{{ "%04d"|format(employee.id) }}\n        </span>',
    new_header.lstrip('\n')
)

# Fix missing closing div for flex items-center gap-6
# Wait, I didn't add a closing div for the extra wrapper, I should find the end of the `<div>` for the left part.
content = content.replace(
    """        <p class="mt-1 text-sm text-white/80 font-medium">
          {{ employee.position }} &middot; {{ employee.department }}
        </p>
      </div>""",
    """        <p class="mt-1 text-sm text-white/80 font-medium">
          {{ employee.position }} &middot; {{ employee.department }}
        </p>
        </div>
      </div>"""
)

with open('templates/view_employee.html', 'w') as f:
    f.write(content)
