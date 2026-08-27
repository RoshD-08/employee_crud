import re

with open('templates/base.html', 'r') as f:
    content = f.read()

# Replace e.key logic with e.code
script_orig = """      if (e.altKey && !e.ctrlKey && !e.shiftKey && !e.metaKey) {
        const key = e.key.toLowerCase();
        let targetUrl = '';
        {% if g.user %}
        switch(key) {
          case 'h': targetUrl = "{{ url_for('list_employees') }}"; break;
          case 'p': targetUrl = "{{ url_for('payroll_dashboard') }}"; break;
          case 'a': targetUrl = "{{ url_for('daily_attendance') }}"; break;
          case 'l': targetUrl = "{{ url_for('advances_loans') }}"; break;
          case 'm': targetUrl = "{{ url_for('employees_map') }}"; break;
          {% if g.user.role == 'Admin' %}
          case 's': targetUrl = "{{ url_for('company_settings') }}"; break;
          {% endif %}
          {% if g.user.role in ['Admin', 'HR'] %}
          case 'n': targetUrl = "{{ url_for('add_employee') }}"; break;
          {% endif %}
        }"""

script_new = """      if (e.altKey && !e.ctrlKey && !e.shiftKey && !e.metaKey) {
        const code = e.code; // Use e.code instead of e.key because Mac Option key alters the typed character (e.g. Option+P = π)
        let targetUrl = '';
        {% if g.user %}
        switch(code) {
          case 'KeyH': targetUrl = "{{ url_for('list_employees') }}"; break;
          case 'KeyP': targetUrl = "{{ url_for('payroll_dashboard') }}"; break;
          case 'KeyA': targetUrl = "{{ url_for('daily_attendance') }}"; break;
          case 'KeyL': targetUrl = "{{ url_for('advances_loans') }}"; break;
          case 'KeyM': targetUrl = "{{ url_for('employees_map') }}"; break;
          {% if g.user.role == 'Admin' %}
          case 'KeyS': targetUrl = "{{ url_for('company_settings') }}"; break;
          {% endif %}
          {% if g.user.role in ['Admin', 'HR'] %}
          case 'KeyN': targetUrl = "{{ url_for('add_employee') }}"; break;
          {% endif %}
        }"""

content = content.replace(script_orig, script_new)

with open('templates/base.html', 'w') as f:
    f.write(content)

