import re

with open('templates/base.html', 'r') as f:
    content = f.read()

# 1. Remove the old user block completely using regex
# Look for <div class="mr-4 flex items-center gap-2 border-r border-white/20 pr-4"> ... </div>
pattern = r'<div class="mr-4 flex items-center gap-2 border-r border-white/20 pr-4">.*?</div>\s*<a href="\{\{ url_for\(\'logout\'\) \}\}".*?</a>\s*</div>'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Let me check what the old block really looks like:
#           <div class="mr-4 flex items-center gap-2 border-r border-white/20 pr-4">
#             <div class="text-right">
#               <div class="text-sm font-semibold text-white leading-tight">{{ g.user.username }}</div>
#               <div class="text-[10px] uppercase tracking-wider text-accent-light opacity-80">{{ g.user.role }}</div>
#             </div>
#             <a href="{{ url_for('logout') }}" class="ml-2 text-xs text-white/50 hover:text-white transition-colors">Logout</a>
#           </div>

pattern_better = r'<div class="mr-4 flex items-center gap-2 border-r border-white/20 pr-4">.*?</a>\s*</div>'
content = re.sub(pattern_better, '', content, flags=re.DOTALL)

new_user_block = """
          <div class="ml-4 pl-4 flex items-center gap-4 border-l border-white/20">
            <div class="text-right hidden sm:block">
              <div class="text-sm font-semibold text-white leading-tight">{{ g.user.username }}</div>
              <div class="text-[10px] uppercase tracking-wider text-accent-light opacity-80">{{ g.user.role }}</div>
            </div>
            <a href="{{ url_for('logout') }}" class="inline-flex items-center bg-rust hover:bg-[#9E3924] transition-colors text-white text-sm font-bold px-6 py-2.5 rounded-md shadow-sm border border-[#7A2A1A]">
              Logout
            </a>
          </div>"""

# 2. Insert new block at the end of the flex container for links
content = re.sub(r'({% if g.user.role in \[\'Admin\', \'HR\'\] %}.*?{% endif %})(\s*{% endif %}\s*</div>)', r'\1' + new_user_block + r'\2', content, flags=re.DOTALL)

with open('templates/base.html', 'w') as f:
    f.write(content)
