import re

with open('templates/daily_attendance.html', 'r') as f:
    content = f.read()

# I need to add </div> after the form
old_form = """  <div class="flex items-center gap-4">
    <a href="{{ url_for('attendance_dashboard') }}" class="text-sm font-medium text-ink/70 hover:text-ink underline underline-offset-2">Monthly Summary</a>
    <form class="flex items-center gap-2 bg-paper p-1.5 rounded-md border border-line shadow-sm" method="GET" action="{{ url_for('daily_attendance') }}" id="dateForm">
    <input type="date" name="date" value="{{ target_date.strftime('%Y-%m-%d') }}" onchange="document.getElementById('dateForm').submit()" class="bg-transparent border-none text-sm focus:ring-0 py-1 px-2 cursor-pointer" />
  </form>
</div>"""

if "  </form>\n</div>" not in content:
    content = content.replace("  </form>\n</div>", "  </form>\n  </div>\n</div>")
    # Actually, let's just do a string replacement
    # Currently it ends with:
    #   </form>
    # </div>
    # Which closes the main mb-6 flex div. But I need to close the inner div too.

