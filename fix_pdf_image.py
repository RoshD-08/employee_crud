import re

with open('templates/profile_pdf.html', 'r') as f:
    content = f.read()

replacement = """
                {% if employee.photo %}
                    <img src="{{ base_dir }}/static/uploads/photos/{{ employee.photo }}" style="width: 70px; height: 70px; border: 1px solid #E2E5EA; display: inline-block;">
                {% else %}
                    <div style="width: 70px; height: 70px; background-color: #F7F8FA; border: 1px solid #E2E5EA; display: inline-block; text-align: center; line-height: 70px; color: #9ca3af; font-size: 8pt;">
                        Photo
                    </div>
                {% endif %}
"""

pattern = r'<div style="width: 70px; height: 70px; background-color: #F7F8FA; border: 1px solid #E2E5EA; display: inline-block; text-align: center; line-height: 70px; color: #9ca3af; font-size: 8pt;">\s*Photo\s*<\/div>'

content = re.sub(pattern, replacement.strip(), content)

with open('templates/profile_pdf.html', 'w') as f:
    f.write(content)
