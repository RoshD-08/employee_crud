import re

with open('app.py', 'r') as f:
    content = f.read()

orig_validation = """    if not employee_category: errors.append("Employee category is required.")"""

new_validation = """    if not employee_category: errors.append("Employee category is required.")
    if not tax_id: errors.append("Tax ID is required.")
    if not epf_number: errors.append("EPF Number is required.")
    if not esi_number: errors.append("ESI Number is required.")"""

content = content.replace(orig_validation, new_validation)

with open('app.py', 'w') as f:
    f.write(content)
