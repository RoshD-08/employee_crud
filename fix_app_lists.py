import re

with open('app.py', 'r') as f:
    content = f.read()

# 1. Add get_list_setting helper
helper_func = """
def get_list_setting(key, default_list):
    val = get_company_setting(key, None)
    if not val:
        return default_list
    return [x.strip() for x in val.split(',') if x.strip()]
"""

# Insert after get_company_setting
content = re.sub(
    r'(def get_company_setting\(setting_key, default_val=None\):.*?return default_val\n)',
    r'\1' + helper_func,
    content,
    flags=re.DOTALL
)

# 2. Update globals
# Wait, if we fetch these globally once, they won't update when changed in settings.
# We must fetch them dynamically in the routes, OR use a context processor.
# A context processor makes them available to all templates!
context_processor = """
@app.context_processor
def inject_globals():
    return {
        "departments": get_list_setting("departments", ["HR", "IT", "Sales", "Operations", "Finance", "Management", "Marketing", "Support"]),
        "employment_types": get_list_setting("employment_types", ["Full-time", "Part-time", "Contract", "Intern"]),
        "employment_statuses": get_list_setting("employment_statuses", ["Active", "On Leave", "Suspended", "Terminated", "Resigned"]),
        "tax_filing_statuses": get_list_setting("social_statuses", ["Single", "Married", "Other"]),
        "genders": get_list_setting("genders", ["Male", "Female", "Other", "Prefer not to say"]),
        "employee_categories": ["Employee", "Labourer"],
        "payment_methods": ["Bank Transfer", "Cash", "Cheque"],
        "attendance_statuses": ["Present", "Absent", "Half-day", "No-pay", "Leave"],
        "leave_types": ["Annual", "Casual", "Medical"]
    }
"""

content = content.replace(
    'app = Flask(__name__)',
    'app = Flask(__name__)\n' + context_processor
)

# 3. Remove the old globals
old_globals = r'DEPARTMENTS = \[.*?\]\nEMPLOYMENT_TYPES = \[.*?\]\nEMPLOYMENT_STATUSES = \[.*?\]\nPAYMENT_METHODS = \[.*?\]\nTAX_FILING_STATUSES = \[.*?\]\nGENDERS = \[.*?\]\nEMPLOYEE_CATEGORIES = \[.*?\]\n\nATTENDANCE_STATUSES = \[.*?\]\nLEAVE_TYPES = \[.*?\]\n'
content = re.sub(old_globals, '', content, flags=re.DOTALL)
# Also try simpler regex in case formatting differs slightly
content = re.sub(r'DEPARTMENTS = \[.*?\].*?LEAVE_TYPES = \[.*?\]\n', '', content, flags=re.DOTALL)

# 4. Update route returns to remove manually passing DEPARTMENTS etc.
# In list_employees
content = re.sub(
    r'departments=DEPARTMENTS,\s*employment_statuses=EMPLOYMENT_STATUSES',
    '',
    content
)
# We might leave a trailing comma, let's just clean it up safely:
content = re.sub(r'selected_status=status,\s*\)', 'selected_status=status)', content)

# In add_employee
content = re.sub(
    r'departments=DEPARTMENTS,\s*employment_types=EMPLOYMENT_TYPES,\s*employment_statuses=EMPLOYMENT_STATUSES,\s*tax_filing_statuses=TAX_FILING_STATUSES,\s*genders=GENDERS,\s*employee_categories=EMPLOYEE_CATEGORIES,\s*payment_methods=PAYMENT_METHODS',
    '',
    content
)
content = re.sub(r'errors=errors,\s*\)', 'errors=errors)', content)
content = re.sub(r'data=data,\s*\)', 'data=data)', content)

# In edit_employee
content = re.sub(
    r'departments=DEPARTMENTS,\s*employment_types=EMPLOYMENT_TYPES,\s*employment_statuses=EMPLOYMENT_STATUSES,\s*tax_filing_statuses=TAX_FILING_STATUSES,\s*genders=GENDERS,\s*employee_categories=EMPLOYEE_CATEGORIES,\s*payment_methods=PAYMENT_METHODS',
    '',
    content
)
content = re.sub(r'errors=errors,\s*\)', 'errors=errors)', content)
content = re.sub(r'employee=employee,\s*\)', 'employee=employee)', content)


# 5. Update company_settings route to handle the new lists
settings_route_old = """def company_settings():
    if request.method == "POST":
        bonus = request.form.get("annual_bonus", "0").strip()
        incentive = request.form.get("monthly_incentive", "0").strip()
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(\"\"\"
                    INSERT INTO company_settings (setting_key, setting_value)
                    VALUES ('annual_bonus', %s)
                    ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value,
                        updated_at = CURRENT_TIMESTAMP;
                \"\"\", (bonus,))
                cur.execute(\"\"\"
                    INSERT INTO company_settings (setting_key, setting_value)
                    VALUES ('monthly_incentive', %s)
                    ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value,
                        updated_at = CURRENT_TIMESTAMP;
                \"\"\", (incentive,))
            conn.commit()"""

settings_route_new = """def company_settings():
    if request.method == "POST":
        bonus = request.form.get("annual_bonus", "0").strip()
        incentive = request.form.get("monthly_incentive", "0").strip()
        
        departments = request.form.get("departments", "").strip()
        employment_types = request.form.get("employment_types", "").strip()
        employment_statuses = request.form.get("employment_statuses", "").strip()
        social_statuses = request.form.get("social_statuses", "").strip()
        genders = request.form.get("genders", "").strip()
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                for key, val in [
                    ('annual_bonus', bonus),
                    ('monthly_incentive', incentive),
                    ('departments', departments),
                    ('employment_types', employment_types),
                    ('employment_statuses', employment_statuses),
                    ('social_statuses', social_statuses),
                    ('genders', genders)
                ]:
                    cur.execute(\"\"\"
                        INSERT INTO company_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value,
                            updated_at = CURRENT_TIMESTAMP;
                    \"\"\", (key, val))
            conn.commit()"""

content = content.replace(settings_route_old, settings_route_new)


with open('app.py', 'w') as f:
    f.write(content)
