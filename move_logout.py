import re

with open('templates/base.html', 'r') as f:
    content = f.read()

# 1. Remove the old user block
old_user_block = """          <div class="mr-4 flex items-center gap-2 border-r border-white/20 pr-4">
            <div class="text-right">
              <div class="text-sm font-semibold text-white leading-tight">{{ g.user.username }}</div>
              <div class="text-[10px] uppercase tracking-wider text-accent-light opacity-80">{{ g.user.role }}</div>
            </div>
            <a href="{{ url_for('logout') }}" class="ml-2 text-xs text-white/50 hover:text-white transition-colors">Logout</a>
          </div>"""
          
content = content.replace(old_user_block, "")

# 2. Insert the new user block at the end, right before the closing {% endif %} for g.user
new_user_block = """
          <div class="ml-4 pl-4 flex items-center gap-4 border-l border-white/20">
            <div class="text-right hidden sm:block">
              <div class="text-sm font-semibold text-white leading-tight">{{ g.user.username }}</div>
              <div class="text-[10px] uppercase tracking-wider text-accent-light opacity-80">{{ g.user.role }}</div>
            </div>
            <a href="{{ url_for('logout') }}" class="inline-flex items-center bg-rust hover:brightness-110 transition-all text-white text-sm font-bold px-5 py-2 rounded-md shadow-sm border border-red-900/30">
              Logout
            </a>
          </div>"""

# Look for the last {% endif %} inside the header's flex container
# We can just replace:
#             </a>
#           {% endif %}
#         {% endif %}
#       </div>

target_to_replace = """            </a>
          {% endif %}
        {% endif %}
      </div>"""

replacement = f"""            </a>
          {{% endif %}}{new_user_block}
        {{% endif %}}
      </div>"""

content = content.replace(target_to_replace, replacement)

# What if Admin is false? Then the last thing is Settings {% endif %}? No, New button is for Admin and HR.
# It's better to use regex to find the end of the `if g.user` block.

