with open('templates/base.html', 'r') as f:
    content = f.read()

nav_item = """          <a href="{{ url_for('advances_loans') }}"
             class="inline-flex items-center gap-2 border border-white/25 hover:bg-white/10 text-white text-sm font-semibold px-4 py-2 rounded-md">
            Advances & Loans
          </a>
"""

if 'advances_loans' not in content:
    target = """          <a href="{{ url_for('payroll_dashboard') }}"
             class="inline-flex items-center gap-2 border border-white/25 hover:bg-white/10 text-white text-sm font-semibold px-4 py-2 rounded-md">
            Payroll
          </a>"""
    content = content.replace(target, target + '\n' + nav_item)
    with open('templates/base.html', 'w') as f:
        f.write(content)
    print("Navbar updated.")
else:
    print("Navbar already updated.")
