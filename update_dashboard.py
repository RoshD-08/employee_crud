import re

def update_file():
    with open('templates/payroll_dashboard.html', 'r') as f:
        content = f.read()

    # Wrap Generate Payroll button
    content = content.replace(
        '''<form method="POST" action="{{ url_for('generate_payroll', year=year, month=month) }}"
                      onsubmit="return confirm('Generate/re-generate payroll for all active employees?');">
                    <button type="submit" class="bg-[#2F6F63] hover:bg-[#204E45] text-white px-4 py-2 rounded-md text-sm font-semibold transition-colors shadow-sm">
                        Generate Payroll
                    </button>
                </form>''',
        '''{% if g.user and g.user.role in ["Admin", "HR"] %}
                <form method="POST" action="{{ url_for('generate_payroll', year=year, month=month) }}"
                      onsubmit="return confirm('Generate/re-generate payroll for all active employees?');">
                    <button type="submit" class="bg-[#2F6F63] hover:bg-[#204E45] text-white px-4 py-2 rounded-md text-sm font-semibold transition-colors shadow-sm">
                        Generate Payroll
                    </button>
                </form>
                {% endif %}'''
    )

    # Wrap Approve All and Bank File and Mark Paid
    # Wait, Bank File and Mark All Paid are inside two different places.
    # In the header:
    bank_file_mark_paid = '''<a href="{{ url_for('generate_bank_file', year=year, month=month) }}"
                   class="bg-white border border-[#E2E5EA] px-4 py-2 rounded-md text-sm font-medium text-[#14181F] hover:bg-gray-50 transition-colors inline-flex items-center shadow-sm">
                    <svg class="w-4 h-4 mr-1.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    Bank File (CSV)
                </a>
                <form method="POST" action="{{ url_for('mark_all_paid', year=year, month=month) }}"
                      onsubmit="return confirm('Mark ALL payslips for {{ month_name }} {{ year }} as paid?');">
                    <button type="submit" class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-md text-sm font-semibold transition-colors inline-flex items-center">
                        &#10003; Mark All Paid
                    </button>
                </form>'''
    
    content = content.replace(bank_file_mark_paid, 
        '''{% if g.user and g.user.role in ["Admin", "Finance"] %}
                <form method="POST" action="{{ url_for('approve_all', year=year, month=month) }}"
                      onsubmit="return confirm('Approve all drafted payrolls for {{ month_name }} {{ year }}?');">
                    <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-semibold transition-colors inline-flex items-center">
                        Approve All
                    </button>
                </form>
                ''' + bank_file_mark_paid + '''
                {% endif %}'''
    )

    # In the bottom block, Bank Payment:
    bank_payment_block = '''<div class="bg-white rounded-lg shadow-sm border border-[#E2E5EA] p-5">
            <h3 class="font-semibold text-gray-700 mb-2">Bank Payment</h3>
            <p class="text-sm text-gray-500 mb-3">Download a CSV bank payment file containing all employee payment details for this month.</p>
            <a href="{{ url_for('generate_bank_file', year=year, month=month) }}"
               class="inline-flex items-center bg-[#2F6F63] hover:bg-[#204E45] text-white px-4 py-2 rounded-md text-sm font-semibold transition-colors">
                <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                Download Bank Payment File
            </a>
        </div>'''
    
    content = content.replace(bank_payment_block, 
        '''{% if g.user and g.user.role in ["Admin", "Finance"] %}\n        ''' + bank_payment_block + '''\n        {% endif %}'''
    )

    with open('templates/payroll_dashboard.html', 'w') as f:
        f.write(content)

update_file()
