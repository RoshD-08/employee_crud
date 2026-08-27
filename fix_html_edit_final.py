import re

with open('templates/edit_employee.html', 'r') as f:
    content = f.read()

# Update form enctype if not already present
if 'enctype="multipart/form-data"' not in content:
    content = content.replace(
        '<form method="POST" action="{{ url_for(\'edit_employee\', employee_id=employee.id) }}">',
        '<form method="POST" action="{{ url_for(\'edit_employee\', employee_id=employee.id) }}" enctype="multipart/form-data">'
    )

photo_html = """
        <div class="col-span-1 md:col-span-2">
          <label class="block text-sm font-semibold text-ink mb-1.5" for="photo">Profile Photo</label>
          <div class="text-xs text-ink/70 mb-2">Square format recommended (200x200 up to 400x400 px), Max 5 MB, Solid neutral background. Allowed: JPG, JPEG, PNG.</div>
          {% if employee.photo %}
          <div class="mb-3">
            <img src="{{ url_for('static', filename='uploads/photos/' ~ employee.photo) }}" alt="Current Photo" class="w-20 h-20 rounded-full object-cover border border-line">
          </div>
          {% endif %}
          <input type="file" id="photo" name="photo" accept=".jpg, .jpeg, .png" class="w-full rounded-md border border-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent bg-surface">
        </div>
"""

# Find the end of Personal Information block to insert the photo
content = content.replace(
    '        </div>\n      </div>\n\n      <!-- Employment Details -->',
    photo_html + '        </div>\n      </div>\n\n      <!-- Employment Details -->'
)

with open('templates/edit_employee.html', 'w') as f:
    f.write(content)

