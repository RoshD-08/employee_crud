import re

def fix_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Fix account_number -> bank_account_number
    content = content.replace('name="account_number"', 'name="bank_account_number"')
    content = content.replace('id="account_number"', 'id="bank_account_number"')
    content = content.replace('for="account_number"', 'for="bank_account_number"')
    content = content.replace('employee.account_number', 'employee.bank_account_number')
    
    # Fix other_allowances -> other_allowance
    content = content.replace('name="other_allowances"', 'name="other_allowance"')
    content = content.replace('id="other_allowances"', 'id="other_allowance"')
    content = content.replace('for="other_allowances"', 'for="other_allowance"')
    content = content.replace('employee.other_allowances', 'employee.other_allowance')

    with open(filename, 'w') as f:
        f.write(content)

fix_file('templates/add_employee.html')
fix_file('templates/edit_employee.html')
