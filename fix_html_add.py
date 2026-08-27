import re

with open('templates/add_employee.html', 'r') as f:
    content = f.read()

# Update form enctype
content = content.replace(
    '<form method="POST" action="{{ url_for(\'add_employee\') }}">',
    '<form method="POST" action="{{ url_for(\'add_employee\') }}" enctype="multipart/form-data">'
)

# Add photo input
photo_html = """
        <div class="mt-4">
          <label class="block text-sm font-semibold text-ink mb-1.5" for="photo">Profile Photo</label>
          <div class="text-xs text-ink/70 mb-2">Square format recommended (200x200 up to 400x400 px), Max 5 MB, Solid neutral background. Allowed: JPG, JPEG, PNG.</div>
          <input type="file" id="photo" name="photo" accept=".jpg, .jpeg, .png" class="w-full rounded-md border border-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent">
        </div>
"""

content = content.replace(
    '        <div class="mt-4">\n          <label class="block text-sm font-semibold text-ink mb-1.5" for="national_id">National ID / NIC</label>',
    photo_html + '        <div class="mt-4">\n          <label class="block text-sm font-semibold text-ink mb-1.5" for="national_id">National ID / NIC</label>'
)

with open('templates/add_employee.html', 'w') as f:
    f.write(content)
