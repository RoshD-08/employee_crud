import re

with open('app.py', 'r') as f:
    content = f.read()

# For add_employee
old_except = """            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                errors.append("An employee with that email already exists.")"""

new_except = """            except psycopg2.errors.UniqueViolation as e:
                conn.rollback()
                err_msg = str(e)
                if "email" in err_msg:
                    errors.append("An employee with that email already exists.")
                elif "tax_id" in err_msg:
                    errors.append("An employee with that Tax ID already exists.")
                elif "epf_number" in err_msg:
                    errors.append("An employee with that EPF Number already exists.")
                elif "esi_number" in err_msg:
                    errors.append("An employee with that ESI Number already exists.")
                else:
                    errors.append("A unique constraint violation occurred.")"""

content = content.replace(old_except, new_except)

with open('app.py', 'w') as f:
    f.write(content)

