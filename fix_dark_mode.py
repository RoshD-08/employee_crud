import re

with open('templates/base.html', 'r') as f:
    content = f.read()

css = """
  <style>
    /* Subtle stamped-grid texture behind the header — a quiet nod to a paper roster/ledger */
    .roster-texture {
      background-image:
        linear-gradient(to right, #ffffff10 1px, transparent 1px),
        linear-gradient(to bottom, #ffffff10 1px, transparent 1px);
      background-size: 22px 22px;
    }

    /* Dark Mode Filter Hack */
    html.dark-theme {
      filter: invert(1) hue-rotate(180deg);
      background-color: #080705; /* inverted paper */
    }
    
    html.dark-theme img,
    html.dark-theme .leaflet-container {
      filter: invert(1) hue-rotate(180deg);
    }
  </style>

  <script>
    // Check local storage for dark mode preference
    if (localStorage.getItem('theme') === 'dark') {
      document.documentElement.classList.add('dark-theme');
    }
  </script>
"""

content = re.sub(r'<style>.*?</style>', css, content, flags=re.DOTALL)

with open('templates/base.html', 'w') as f:
    f.write(content)
