import re

with open('templates/view_employee.html', 'r') as f:
    content = f.read()

btn_html = """
        <a href="{{ url_for('download_profile_pdf', id=employee.id) }}"
           class="rounded-md border border-white/25 hover:bg-white/10 transition-colors text-white text-sm font-semibold px-4 py-2 flex items-center gap-1.5" title="Download PDF">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          PDF
        </a>
"""

# Wait, a better icon for download PDF:
btn_html = """
        <a href="{{ url_for('download_profile_pdf', id=employee.id) }}"
           class="rounded-md border border-white/25 hover:bg-white/10 transition-colors text-white text-sm font-semibold px-4 py-2 flex items-center gap-1.5" title="Download Profile PDF">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          PDF
        </a>
"""

content = content.replace(
    '<div class="flex items-center gap-2 shrink-0">',
    '<div class="flex items-center gap-2 shrink-0">\n' + btn_html
)

with open('templates/view_employee.html', 'w') as f:
    f.write(content)

