import re

def extract_inputs(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # regex to find name="..."
    names = re.findall(r'name=["\']([^"\']+)["\']', content)
    # unique names
    return set(names)

add_names = extract_inputs('templates/add_employee.html')
edit_names = extract_inputs('templates/edit_employee.html')

backend_names = {
    "first_name", "last_name", "email", "phone", "date_of_birth", "gender", 
    "national_id", "emergency_contact_name", "emergency_contact_phone", 
    "department", "position", "employment_type", "hire_date", "employment_status", 
    "employee_category", "salary", "housing_allowance", "transport_allowance", 
    "medical_allowance", "other_allowance", "payment_method", "bank_name", 
    "bank_branch", "bank_account_number", "tax_id", "epf_number", "esi_number", 
    "tax_filing_status", "address", "latitude", "longitude", 
    "annual_leave_allowed", "casual_leave_allowed", "medical_leave_allowed"
}

print("Missing in add_employee.html:", backend_names - add_names)
print("Missing in edit_employee.html:", backend_names - edit_names)

print("Extra in add_employee.html:", add_names - backend_names)
print("Extra in edit_employee.html:", edit_names - backend_names)
