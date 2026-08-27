import re

with open('templates/settings.html', 'r') as f:
    content = f.read()

# I will insert the new System Settings section before the form button, or as a completely separate block.
# Actually, the entire settings.html is currently wrapped in a <form> for the Bonus.
# I should put the System Settings above or below it.

new_section = """
    <!-- System Settings Section -->
    <div class="bg-white rounded-lg border border-[#E2E5EA] shadow-sm overflow-hidden mb-6">
        <div class="p-6">
            <h2 class="text-lg font-bold text-[#14181F] mb-4 border-b border-[#E2E5EA] pb-2">System Settings</h2>
            
            <div class="flex items-center justify-between">
                <div>
                    <h3 class="text-sm font-semibold text-ink">Appearance</h3>
                    <p class="text-xs text-[#14181F]/70 mt-1">Toggle between light and dark theme for the interface.</p>
                </div>
                
                <button type="button" id="theme-toggle" class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 bg-gray-200">
                    <span class="sr-only">Toggle Dark Mode</span>
                    <span id="theme-toggle-knob" class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out translate-x-0"></span>
                </button>
            </div>
        </div>
    </div>
"""

content = content.replace(
    '<div class="bg-white rounded-lg border border-[#E2E5EA] shadow-sm overflow-hidden">',
    new_section + '\n    <div class="bg-white rounded-lg border border-[#E2E5EA] shadow-sm overflow-hidden">'
)

js = """
{% block scripts %}
<script>
    const toggleBtn = document.getElementById('theme-toggle');
    const toggleKnob = document.getElementById('theme-toggle-knob');
    
    function updateToggleState() {
        if (document.documentElement.classList.contains('dark-theme')) {
            toggleBtn.classList.remove('bg-gray-200');
            toggleBtn.classList.add('bg-accent');
            toggleKnob.classList.remove('translate-x-0');
            toggleKnob.classList.add('translate-x-5');
        } else {
            toggleBtn.classList.add('bg-gray-200');
            toggleBtn.classList.remove('bg-accent');
            toggleKnob.classList.add('translate-x-0');
            toggleKnob.classList.remove('translate-x-5');
        }
    }

    // Initialize toggle state on page load
    updateToggleState();

    toggleBtn.addEventListener('click', function() {
        if (document.documentElement.classList.contains('dark-theme')) {
            document.documentElement.classList.remove('dark-theme');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
        }
        updateToggleState();
    });
</script>
{% endblock %}
"""

content = content.replace('{% endblock %}', js)

with open('templates/settings.html', 'w') as f:
    f.write(content)
