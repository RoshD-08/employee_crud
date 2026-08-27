import re

with open('templates/profile_pdf.html', 'r') as f:
    content = f.read()

bad_css = """            @top-right {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 8pt;
                color: #6b7280;
            }"""

content = content.replace(bad_css, '')

with open('templates/profile_pdf.html', 'w') as f:
    f.write(content)
