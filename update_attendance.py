import re

def update_file():
    with open('templates/attendance.html', 'r') as f:
        content = f.read()

    # Wrap the save button
    content = content.replace(
        '<button type="submit" class="bg-[#2F6F63] hover:bg-[#204E45] text-white px-6 py-2 rounded-md font-medium text-sm transition-colors shadow-sm">\n                   Save Attendance\n                </button>',
        '{% if g.user and g.user.role in ["Admin", "HR"] %}\n                <button type="submit" class="bg-[#2F6F63] hover:bg-[#204E45] text-white px-6 py-2 rounded-md font-medium text-sm transition-colors shadow-sm">\n                   Save Attendance\n                </button>\n                {% endif %}'
    )

    # Disable inputs if Finance
    # Since there are many inputs, let's just add {% if g.user and g.user.role == "Finance" %}disabled{% endif %} to all inputs/selects in the loop.
    content = re.sub(r'(<input [^>]+)(>)', r'\1 {% if g.user and g.user.role == "Finance" %}disabled{% endif %} \2', content)
    content = re.sub(r'(<select [^>]+)(>)', r'\1 {% if g.user and g.user.role == "Finance" %}disabled{% endif %} \2', content)

    with open('templates/attendance.html', 'w') as f:
        f.write(content)

update_file()
