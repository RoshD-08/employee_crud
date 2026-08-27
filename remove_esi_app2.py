import re

with open('app.py', 'r') as f:
    content = f.read()

content = re.sub(r'\s*elif "esi_number" in err_msg:\s*errors\.append\("An employee with that ESI Number already exists\."\)', '', content)

with open('app.py', 'w') as f:
    f.write(content)
