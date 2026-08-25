with open('templates/daily_attendance.html', 'r') as f:
    content = f.read()

header = """  <form class="flex items-center gap-2 bg-paper p-1.5 rounded-md border border-line shadow-sm" method="GET" action="{{ url_for('daily_attendance') }}" id="dateForm">"""

new_header = """  <div class="flex items-center gap-4">
    <a href="{{ url_for('attendance_dashboard') }}" class="text-sm font-medium text-ink/70 hover:text-ink underline underline-offset-2">Monthly Summary</a>
    <form class="flex items-center gap-2 bg-paper p-1.5 rounded-md border border-line shadow-sm" method="GET" action="{{ url_for('daily_attendance') }}" id="dateForm">"""

content = content.replace(header, new_header)

with open('templates/daily_attendance.html', 'w') as f:
    f.write(content)
