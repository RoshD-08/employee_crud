import re

def process_file(filename):
    with open(filename, 'r') as f:
        content = f.read()

    # The HTML for the ESI input block looks something like:
    # <div>
    #   <label ... for="esi_number">ESI Number <span class="text-rust">*</span></label>
    #   <input ... id="esi_number" name="esi_number" ...>
    # </div>
    # 
    # Or in edit_employee it might not be wrapped in div if the grid is direct, wait.
    
    # Actually, in add_employee and edit_employee it is wrapped in <div>.
    # Let's just find the label and input and remove their surrounding div.
    pattern = r'<div>\s*<label[^>]*for="esi_number"[^>]*>.*?</label>\s*<input[^>]*id="esi_number"[^>]*>\s*</div>'
    
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    with open(filename, 'w') as f:
        f.write(content)

process_file('templates/add_employee.html')
process_file('templates/edit_employee.html')

