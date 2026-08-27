import re

with open('app.py', 'r') as f:
    content = f.read()

# 1. Remove form.get
content = re.sub(r'\s*esi_number\s*=\s*form\.get\("esi_number", ""\)\.strip\(\)\n', '\n', content)

# 2. Remove validation
content = re.sub(r'\s*if not esi_number: errors\.append\("ESI Number is required\."\)\n', '\n', content)

# 3. Remove from data dictionary
content = content.replace('"esi_number": esi_number or None, ', '')

# 4. Remove from _INSERT_COLS list
content = content.replace('"esi_number", ', '')

# 5. Remove unique violation handling for esi_number
content = re.sub(r'\s*elif "esi_number" in err_msg:\s*flash\("An employee with this ESI Number already exists\.", "error"\)', '', content)

with open('app.py', 'w') as f:
    f.write(content)
