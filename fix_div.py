with open('templates/daily_attendance.html', 'r') as f:
    content = f.read()

old_str = """    <input type="date" name="date" value="{{ target_date.strftime('%Y-%m-%d') }}" onchange="document.getElementById('dateForm').submit()" class="bg-transparent border-none text-sm focus:ring-0 py-1 px-2 cursor-pointer" />
  </form>
</div>"""

new_str = """    <input type="date" name="date" value="{{ target_date.strftime('%Y-%m-%d') }}" onchange="document.getElementById('dateForm').submit()" class="bg-transparent border-none text-sm focus:ring-0 py-1 px-2 cursor-pointer" />
  </form>
  </div>
</div>"""

content = content.replace(old_str, new_str)

with open('templates/daily_attendance.html', 'w') as f:
    f.write(content)
