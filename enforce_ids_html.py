import re

def process_file(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # Tax ID
    content = content.replace(
        '<label class="block text-sm font-semibold text-ink mb-1.5" for="tax_id">Tax ID (TIN/PAN)</label>',
        '<label class="block text-sm font-semibold text-ink mb-1.5" for="tax_id">Tax ID (TIN/PAN) <span class="text-rust">*</span></label>'
    )
    content = re.sub(
        r'(<input type="text" id="tax_id" name="tax_id".*?value="\{\{ employee\.tax_id or \'\' \}\}")(.*?>)',
        r'\1 required\2',
        content
    )
    
    # EPF Number
    content = content.replace(
        '<label class="block text-sm font-semibold text-ink mb-1.5" for="epf_number">EPF Number</label>',
        '<label class="block text-sm font-semibold text-ink mb-1.5" for="epf_number">EPF Number <span class="text-rust">*</span></label>'
    )
    content = re.sub(
        r'(<input type="text" id="epf_number" name="epf_number".*?value="\{\{ employee\.epf_number or \'\' \}\}")(.*?>)',
        r'\1 required\2',
        content
    )

    # ESI Number
    content = content.replace(
        '<label class="block text-sm font-semibold text-ink mb-1.5" for="esi_number">ESI Number</label>',
        '<label class="block text-sm font-semibold text-ink mb-1.5" for="esi_number">ESI Number <span class="text-rust">*</span></label>'
    )
    content = re.sub(
        r'(<input type="text" id="esi_number" name="esi_number".*?value="\{\{ employee\.esi_number or \'\' \}\}")(.*?>)',
        r'\1 required\2',
        content
    )

    with open(filename, 'w') as f:
        f.write(content)

process_file('templates/add_employee.html')
process_file('templates/edit_employee.html')

