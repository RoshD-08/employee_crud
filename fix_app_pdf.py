import re

with open('app.py', 'r') as f:
    content = f.read()

# I will find the block of decorators and remove the extra ones.
# The messed up part looks exactly like:
'''
@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/pdf")
@login_required
@role_required("Admin", "HR")

@app.route("/employees/<int:id>/pdf")
'''
# Actually the `sed` showed:
'''
@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/pdf")
@login_required

@app.route("/employees/<int:id>/pdf")
'''

content = content.replace('@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/pdf")\n@login_required\n\n@app.route("/employees/<int:id>/pdf")', '@app.route("/employees/<int:id>/pdf")')

# Let's also check for role_required if it was left
content = content.replace('@app.route("/payroll/<int:year>/<int:month>/<int:employee_id>/pdf")\n@login_required\n@role_required("Admin", "HR")\n\n@app.route("/employees/<int:id>/pdf")', '@app.route("/employees/<int:id>/pdf")')

with open('app.py', 'w') as f:
    f.write(content)
