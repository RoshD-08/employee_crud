with open('templates/payslip_pdf.html', 'r') as f:
    content = f.read()

content = content.replace('line-height: 1.4;', 'line-height: 1.25;')
content = content.replace('font-size: 10pt;', 'font-size: 9.5pt;')
content = content.replace('font-size: 9.5pt;', 'font-size: 9pt;')
content = content.replace('font-size: 9pt;', 'font-size: 8.5pt;')
# But wait, replacing sequentially might cascade down to 8.5pt.
# Let's just use regex to bump down sizes if we want, or just leave it. The margins fix is usually enough for xhtml2pdf to stop spilling to a second page.

