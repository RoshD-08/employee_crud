import re

with open('templates/payslip_pdf.html', 'r') as f:
    content = f.read()

# 1. Page margin
content = re.sub(r'@page \{ size: A4; margin: .*?; \}', '@page { size: A4; margin: 1cm 1cm; }', content)

# 2. Font sizes
content = content.replace('font-size: 10pt;', 'font-size: 8.5pt;')
content = content.replace('font-size: 9.5pt;', 'font-size: 8.5pt;')
content = content.replace('font-size: 9pt;', 'font-size: 8pt;')
content = content.replace('font-size: 26pt;', 'font-size: 18pt;')
content = content.replace('font-size: 16pt;', 'font-size: 14pt;')
content = content.replace('font-size: 12pt;', 'font-size: 10pt;')
content = content.replace('font-size: 20pt;', 'font-size: 16pt;')
content = content.replace('font-size: 14pt;', 'font-size: 12pt;')
content = content.replace('line-height: 1.4;', 'line-height: 1.2;')

# 3. Margins
content = content.replace('margin-bottom: 15px;', 'margin-bottom: 8px;')
content = content.replace('margin-bottom: 30px;', 'margin-bottom: 10px;')
content = content.replace('margin-bottom: 20px;', 'margin-bottom: 10px;')
content = content.replace('margin-top: 25px;', 'margin-top: 10px;')
content = content.replace('margin-top: 50px;', 'margin-top: 15px;')
content = content.replace('margin: 20px 0 10px 0;', 'margin: 10px 0 5px 0;')
content = content.replace('margin: 15px 0 8px 0;', 'margin: 10px 0 5px 0;')

# 4. Paddings
content = content.replace('padding-bottom: 20px;', 'padding-bottom: 5px;')
content = content.replace('padding-bottom: 10px;', 'padding-bottom: 5px;')
content = content.replace('padding: 15px 25px;', 'padding: 8px 15px;')
content = content.replace('padding: 10px 10px 10px 12px;', 'padding: 5px 5px 5px 8px;')
content = content.replace('padding: 6px 10px;', 'padding: 3px 6px;')
content = content.replace('padding: 8px 12px;', 'padding: 3px 6px;')
content = content.replace('padding: 10px 12px;', 'padding: 3px 6px;')
content = content.replace('padding: 6px 0;', 'padding: 2px 0;')
content = content.replace('padding-top: 6px; padding-bottom: 6px;', 'padding-top: 3px; padding-bottom: 3px;')
content = content.replace('padding-top: 20px;', 'padding-top: 10px;')

# 5. Ensure line breaks in HTML are removed or reduced
content = content.replace('<br><br>', '<br>')

with open('templates/payslip_pdf.html', 'w') as f:
    f.write(content)

