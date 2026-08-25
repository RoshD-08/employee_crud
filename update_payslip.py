import re

def update_file():
    with open('templates/payslip.html', 'r') as f:
        content = f.read()

    # Mark as paid section
    mark_paid_pattern = r'(<form method="POST" action="\{\{ url_for\(\'mark_payslip_paid\'.*?</form>)'
    
    # We want to add Approve button if status is Draft, and Mark as Paid if status is Approved.
    # Currently it's:
    # {% if payslip.payment_status == 'Paid' %}
    # ...
    # {% else %}
    #   <form method="POST" action="{{ url_for('mark_payslip_paid' ...
    #   ...
    # {% endif %}

    # I'll replace the whole else block.
    replacement = """{% else %}
              {% if g.user and g.user.role in ["Admin", "Finance"] %}
                {% if payslip.status == 'Draft' %}
                  <form method="POST" action="{{ url_for('approve_payslip', year=year, month=month, employee_id=employee.id) }}">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-semibold transition-colors">
                      Approve Payslip
                    </button>
                  </form>
                {% elif payslip.status == 'Approved' %}
                  <form method="POST" action="{{ url_for('mark_payslip_paid', year=year, month=month, employee_id=employee.id) }}"
                        onsubmit="return confirm('Mark this payslip as paid?');">
                    <button type="submit" class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-md text-sm font-semibold transition-colors">
                      &#10003; Mark as Paid
                    </button>
                  </form>
                {% endif %}
              {% endif %}
            {% endif %}"""

    content = re.sub(r'\{%\s*else\s*%\}\s*<form method="POST" action="\{\{\s*url_for\(\'mark_payslip_paid\'.*?</form>\s*\{%\s*endif\s*%\}', replacement, content, flags=re.DOTALL)

    # Hide edit form
    edit_form_pattern = r'(<!-- Editable Deductions Form.*?</div>\s*</div>)'
    content = re.sub(edit_form_pattern, r'{% if g.user and g.user.role in ["Admin", "HR"] and payslip.status == "Draft" %}\n\1\n{% endif %}', content, flags=re.DOTALL)

    with open('templates/payslip.html', 'w') as f:
        f.write(content)

update_file()
