import re

with open('templates/settings.html', 'r') as f:
    content = f.read()

new_form_content = """
            <h2 class="text-lg font-bold text-[#14181F] mb-4 border-b border-[#E2E5EA] pb-2">Dropdown Lists & Categories</h2>
            
            <div class="space-y-6 mb-8">
                <div>
                    <label for="departments" class="block text-sm font-semibold text-ink mb-1.5">Departments</label>
                    <textarea id="departments" name="departments" rows="2" class="w-full rounded-md border border-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent">{{ ', '.join(departments) }}</textarea>
                    <p class="mt-1.5 text-xs text-[#14181F]/70">Comma separated values (e.g., HR, IT, Sales)</p>
                </div>
                
                <div>
                    <label for="employment_types" class="block text-sm font-semibold text-ink mb-1.5">Employment Types</label>
                    <input type="text" id="employment_types" name="employment_types" value="{{ ', '.join(employment_types) }}" class="w-full rounded-md border border-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent">
                </div>
                
                <div>
                    <label for="employment_statuses" class="block text-sm font-semibold text-ink mb-1.5">Employment Statuses</label>
                    <input type="text" id="employment_statuses" name="employment_statuses" value="{{ ', '.join(employment_statuses) }}" class="w-full rounded-md border border-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent">
                </div>
                
                <div>
                    <label for="social_statuses" class="block text-sm font-semibold text-ink mb-1.5">Social Statuses</label>
                    <input type="text" id="social_statuses" name="social_statuses" value="{{ ', '.join(tax_filing_statuses) }}" class="w-full rounded-md border border-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent">
                </div>
                
                <div>
                    <label for="genders" class="block text-sm font-semibold text-ink mb-1.5">Genders</label>
                    <input type="text" id="genders" name="genders" value="{{ ', '.join(genders) }}" class="w-full rounded-md border border-line px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40 focus:border-accent">
                </div>
            </div>

            <h2 class="text-lg font-bold text-[#14181F] mb-4 border-b border-[#E2E5EA] pb-2">Bonus & Incentives</h2>
"""

content = content.replace(
    '<h2 class="text-lg font-bold text-[#14181F] mb-4 border-b border-[#E2E5EA] pb-2">Bonus & Incentives</h2>',
    new_form_content
)

with open('templates/settings.html', 'w') as f:
    f.write(content)
