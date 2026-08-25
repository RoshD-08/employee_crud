import re

with open('templates/payslip_pdf.html', 'r') as f:
    content = f.read()

# Reduce margins to save vertical space
content = content.replace('margin-bottom: 30px;', 'margin-bottom: 15px;')
content = content.replace('margin-bottom: 25px;', 'margin-bottom: 15px;')
content = content.replace('margin-top: 50px;', 'margin-top: 25px;')
content = content.replace('margin-top: 20px;', 'margin-top: 10px;')
content = content.replace('margin: 20px 0 10px 0;', 'margin: 15px 0 8px 0;')
content = content.replace('padding-bottom: 20px;', 'padding-bottom: 10px;')

# Reduce padding in tables
content = content.replace('padding: 8px 12px;', 'padding: 6px 10px;')
content = content.replace('padding: 10px 12px;', 'padding: 6px 10px;')
content = content.replace('padding-top: 10px; padding-bottom: 10px;', 'padding-top: 6px; padding-bottom: 6px;')

# Page margin
content = content.replace('margin: 1.5cm 1.5cm;', 'margin: 1.2cm 1.2cm;')

with open('templates/payslip_pdf.html', 'w') as f:
    f.write(content)

