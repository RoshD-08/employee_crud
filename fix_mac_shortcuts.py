import re

with open('templates/base.html', 'r') as f:
    content = f.read()

# Add a class to the Alt kbd elements so we can easily target them with JS
content = content.replace(
    '<kbd class="bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>',
    '<kbd class="shortcut-modifier bg-gray-200 text-gray-700 px-1.5 py-0.5 rounded border border-gray-300">Alt</kbd>'
)

# Add the OS detection script
script_addition = """
    // Update shortcut keys for Mac users
    if (navigator.platform.toUpperCase().indexOf('MAC') >= 0) {
      document.querySelectorAll('.shortcut-modifier').forEach(function(el) {
        el.textContent = 'Option ⌥';
      });
    }
"""

content = content.replace(
    'const key = e.key.toLowerCase();',
    script_addition + '\n        const key = e.key.toLowerCase();'
)

# Actually, the script addition should happen when the page loads, not inside the keydown listener!
content = content.replace(
    script_addition + '\n        const key = e.key.toLowerCase();',
    'const key = e.key.toLowerCase();'
)

correct_script_addition = """
    // Update shortcut keys for Mac users
    if (navigator.platform.toUpperCase().indexOf('MAC') >= 0) {
      document.querySelectorAll('.shortcut-modifier').forEach(function(el) {
        el.textContent = 'Option ⌥';
      });
    }
"""

content = content.replace(
    "document.addEventListener('keydown', function(e) {",
    correct_script_addition + "\n    document.addEventListener('keydown', function(e) {"
)

with open('templates/base.html', 'w') as f:
    f.write(content)

