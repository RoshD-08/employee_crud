import re

with open('templates/profile_pdf.html', 'r') as f:
    content = f.read()

# I will find the second table and replace it completely.
# The table starts with <table style="width: 100%; margin-bottom: 10px;">
# and ends right before <h2>Personal Information</h2>

pattern = r'<table style="width: 100%; margin-bottom: 10px;">.*?<\/table>\s*<h2>Personal Information<\/h2>'

new_layout = """<table style="width: 100%; margin-bottom: 15px;">
        <tr>
            <td style="width: 120px; vertical-align: top;">
                {% if employee.photo %}
                    <img src="{{ base_dir }}/static/uploads/photos/{{ employee.photo }}" style="width: 110px; height: 110px; border: 1px solid #E2E5EA;">
                {% else %}
                    <div style="width: 110px; height: 110px; background-color: #F7F8FA; border: 1px solid #E2E5EA; text-align: center; line-height: 110px; color: #9ca3af; font-size: 9pt;">
                        Photo
                    </div>
                {% endif %}
            </td>
            <td style="vertical-align: top; padding-left: 10px; padding-top: 5px;">
                <h1 style="font-size: 18pt; margin: 0; padding: 0; color: #14181F; margin-bottom: 8px;">{{ employee.first_name }} {{ employee.last_name }}</h1>
                <div style="font-size: 11pt; color: #4b5563; margin-bottom: 5px;">{{ employee.position }} — {{ employee.department }}</div>
                <div style="font-size: 11pt; color: #2F6F63; font-weight: bold;">EMP-{{ "%04d"|format(employee.id) }}</div>
            </td>
        </tr>
    </table>

    <h2>Personal Information</h2>"""

content = re.sub(pattern, new_layout, content, flags=re.DOTALL)

with open('templates/profile_pdf.html', 'w') as f:
    f.write(content)
