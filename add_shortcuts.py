import re

with open('templates/base.html', 'r') as f:
    content = f.read()

# Replace footer
footer_orig = """  <footer class="border-t border-line">
    <div class="w-full px-4 sm:px-6 lg:px-8 py-5 text-xs text-ink/50 font-mono">
      Payroll System &middot; internal records
    </div>
  </footer>"""

footer_new = """  <footer class="border-t border-line mt-auto">
    <div class="w-full px-4 sm:px-6 lg:px-8 py-5 text-xs text-ink/50 font-mono flex flex-col md:flex-row justify-between items-center gap-4">
      <span>Payroll System &middot; internal records</span>
      {% if g.user %}
      <div class="flex flex-wrap justify-center gap-3 text-[10px] sm:text-xs">
        <span class="flex items-center gap-1"><kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>+<kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">H</kbd> Home</span>
        <span class="flex items-center gap-1"><kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>+<kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">P</kbd> Payroll</span>
        <span class="flex items-center gap-1"><kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>+<kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">A</kbd> Attendance</span>
        <span class="flex items-center gap-1"><kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>+<kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">L</kbd> Loans</span>
        <span class="flex items-center gap-1"><kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>+<kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">M</kbd> Map</span>
        {% if g.user.role == 'Admin' %}
        <span class="flex items-center gap-1"><kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>+<kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">S</kbd> Settings</span>
        {% endif %}
        {% if g.user.role in ['Admin', 'HR'] %}
        <span class="flex items-center gap-1"><kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>+<kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">N</kbd> New</span>
        {% endif %}
      </div>
      {% endif %}
    </div>
  </footer>"""

content = content.replace(footer_orig, footer_new)

# Add scripts block
script_new = """
  {% block scripts %}
  <script>
    document.addEventListener('keydown', function(e) {
      // Ignore if user is typing in an input or textarea
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
      
      if (e.altKey && !e.ctrlKey && !e.shiftKey && !e.metaKey) {
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
        }
        {% endif %}
        
        if (targetUrl) {
          e.preventDefault();
          window.location.href = targetUrl;
        }
      }
    });
  </script>
  {% endblock %}
</body>"""

content = content.replace("  {% block scripts %}{% endblock %}\n</body>", script_new)

with open('templates/base.html', 'w') as f:
    f.write(content)
