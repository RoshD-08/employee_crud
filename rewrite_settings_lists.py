import re

with open('templates/settings.html', 'r') as f:
    content = f.read()

# Pattern to extract the Dropdown Lists block
pattern = r'<h2 class="text-lg font-bold text-\[\#14181F\] mb-4 border-b border-\[\#E2E5EA\] pb-2">Dropdown Lists & Categories</h2>.*?<h2 class="text-lg font-bold text-\[\#14181F\] mb-4 border-b border-\[\#E2E5EA\] pb-2">Bonus & Incentives</h2>'

def block(id, label, var):
    return f"""
                <div class="bg-paper/50 rounded-lg p-4 border border-line">
                    <label class="block text-sm font-semibold text-ink mb-3">{label}</label>
                    <input type="hidden" id="hidden_{id}" name="{id}" value="{{{{ ', '.join({var}) }}}}">
                    
                    <ul id="ul_{id}" class="space-y-2 mb-3"></ul>
                    
                    <div class="flex gap-2">
                        <input type="text" id="add_{id}" class="flex-1 rounded-md border border-line px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent bg-white" placeholder="Type new item..." onkeydown="if(event.key === 'Enter') {{ event.preventDefault(); addItem('{id}'); }}">
                        <button type="button" onclick="addItem('{id}')" class="bg-accent hover:bg-accent-dark text-white text-sm font-semibold px-4 py-1.5 rounded-md transition-colors shadow-sm">Add</button>
                    </div>
                </div>
"""

new_block = f"""<h2 class="text-lg font-bold text-[#14181F] mb-4 border-b border-[#E2E5EA] pb-2">Dropdown Lists & Categories</h2>
            
            <div class="space-y-5 mb-8">
{block('departments', 'Departments', 'departments')}
{block('employment_types', 'Employment Types', 'employment_types')}
{block('employment_statuses', 'Employment Statuses', 'employment_statuses')}
{block('social_statuses', 'Social Statuses', 'tax_filing_statuses')}
{block('genders', 'Genders', 'genders')}
            </div>

            <h2 class="text-lg font-bold text-[#14181F] mb-4 border-b border-[#E2E5EA] pb-2">Bonus & Incentives</h2>"""

content = re.sub(pattern, new_block, content, flags=re.DOTALL)


# Now add the JavaScript
js = """
    // List editor logic
    const lists = ['departments', 'employment_types', 'employment_statuses', 'social_statuses', 'genders'];

    function renderList(listName) {
        const hiddenInput = document.getElementById('hidden_' + listName);
        const ul = document.getElementById('ul_' + listName);
        ul.innerHTML = '';

        let items = hiddenInput.value.split(',').map(i => i.trim()).filter(i => i);
        
        if (items.length === 0) {
            ul.innerHTML = '<li class="text-xs text-ink/50 italic py-1">No items added.</li>';
            return;
        }

        items.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'flex justify-between items-center bg-white border border-line px-3 py-1.5 rounded-md shadow-sm text-sm';
            
            const textSpan = document.createElement('span');
            textSpan.textContent = item;
            textSpan.className = 'font-medium text-ink';
            
            const btnDiv = document.createElement('div');
            btnDiv.className = 'flex items-center gap-3 border-l border-line pl-3 ml-3';
            
            const editBtn = document.createElement('button');
            editBtn.type = 'button';
            editBtn.innerHTML = 'Edit';
            editBtn.className = 'text-accent hover:text-accent-dark text-xs font-semibold';
            editBtn.onclick = () => editItem(listName, index);
            
            const delBtn = document.createElement('button');
            delBtn.type = 'button';
            delBtn.innerHTML = 'Delete';
            delBtn.className = 'text-rust hover:text-[#913623] text-xs font-semibold';
            delBtn.onclick = () => deleteItem(listName, index);
            
            btnDiv.appendChild(editBtn);
            btnDiv.appendChild(delBtn);
            
            li.appendChild(textSpan);
            li.appendChild(btnDiv);
            ul.appendChild(li);
        });
    }

    function addItem(listName) {
        const addInput = document.getElementById('add_' + listName);
        const hiddenInput = document.getElementById('hidden_' + listName);
        const val = addInput.value.trim();
        
        if (val) {
            let items = hiddenInput.value.split(',').map(i => i.trim()).filter(i => i);
            if (!items.includes(val)) {
                items.push(val);
                hiddenInput.value = items.join(', ');
                addInput.value = '';
                renderList(listName);
            } else {
                alert("Item already exists!");
            }
        }
    }

    function editItem(listName, index) {
        const hiddenInput = document.getElementById('hidden_' + listName);
        let items = hiddenInput.value.split(',').map(i => i.trim()).filter(i => i);
        
        const newVal = prompt("Edit item:", items[index]);
        if (newVal !== null && newVal.trim() !== '') {
            const trimmed = newVal.trim();
            if (trimmed !== items[index] && items.includes(trimmed)) {
                alert("This item already exists!");
                return;
            }
            items[index] = trimmed;
            hiddenInput.value = items.join(', ');
            renderList(listName);
        }
    }

    function deleteItem(listName, index) {
        const hiddenInput = document.getElementById('hidden_' + listName);
        let items = hiddenInput.value.split(',').map(i => i.trim()).filter(i => i);
        
        if (confirm('Are you sure you want to delete "' + items[index] + '"?')) {
            items.splice(index, 1);
            hiddenInput.value = items.join(', ');
            renderList(listName);
        }
    }

    // Initialize lists
    document.addEventListener('DOMContentLoaded', () => {
        lists.forEach(renderList);
    });
"""

content = content.replace('updateToggleState();\n    });', 'updateToggleState();\n    });\n' + js)

with open('templates/settings.html', 'w') as f:
    f.write(content)

