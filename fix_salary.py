import re

def fix_file(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Change basic_salary to salary in name, id, and value
    content = content.replace('name="basic_salary"', 'name="salary"')
    content = content.replace('id="basic_salary"', 'id="salary"')
    content = content.replace('for="basic_salary"', 'for="salary"')
    content = content.replace('employee.basic_salary', 'employee.salary')
    
    with open(filename, 'w') as f:
        f.write(content)

fix_file('templates/add_employee.html')
fix_file('templates/edit_employee.html')
