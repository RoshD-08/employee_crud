import re

with open('templates/attendance.html', 'r') as f:
    content = f.read()

# Replace onchange calls
content = content.replace(
    "calcOT({{ day.date.day }}, {{ 'true' if day.is_sunday else 'false' }})",
    "calcOT({{ day.date.day }}, {{ 'true' if day.is_sunday else 'false' }}, {{ 'true' if day.date.weekday() == 5 else 'false' }})"
)

# Disable the checkboxes so they are read-only (since backend auto-calculates)
# We will just visually disable them so the user knows it's auto.
# Actually, the user can change them if we don't disable, but backend overrides.
# Let's add disabled visually if we want, or just leave them.
# The user might wonder why they can't click them. Let's make them disabled but visually distinct, or just add `onclick="return false;"`
content = content.replace('name="day_{{ day.date.day }}_late"', 'name="day_{{ day.date.day }}_late" onclick="return false;"')
content = content.replace('name="day_{{ day.date.day }}_early"', 'name="day_{{ day.date.day }}_early" onclick="return false;"')

# Replace the script block
old_script = """<script>
function calcOT(dayNum, isSunday) {
    const arrInput = document.querySelector(`[name="day_${dayNum}_arrival"]`);
    const depInput = document.querySelector(`[name="day_${dayNum}_departure"]`);
    
    if (!arrInput || !depInput) return;
    
    const arr = arrInput.value;
    const dep = depInput.value;
    
    if (arr && dep) {
        const [ah, am] = arr.split(':').map(Number);
        const [dh, dm] = dep.split(':').map(Number);
        let worked = (dh + dm/60) - (ah + am/60);
        let ot = Math.max(0, worked - 8);
        document.getElementById(`ot_display_${dayNum}`).textContent = ot.toFixed(1);
    } else {
        document.getElementById(`ot_display_${dayNum}`).textContent = '0.0';
    }
}"""

new_script = """<script>
function calcOT(dayNum, isSunday, isSaturday) {
    const arrInput = document.querySelector(`[name="day_${dayNum}_arrival"]`);
    const depInput = document.querySelector(`[name="day_${dayNum}_departure"]`);
    const lateCheck = document.querySelector(`[name="day_${dayNum}_late"]`);
    const earlyCheck = document.querySelector(`[name="day_${dayNum}_early"]`);
    const otDisplay = document.getElementById(`ot_display_${dayNum}`);
    
    if (!arrInput || !depInput) return;
    
    const arr = arrInput.value;
    const dep = depInput.value;
    
    if (arr && dep) {
        const [ah, am] = arr.split(':').map(Number);
        const [dh, dm] = dep.split(':').map(Number);
        
        let arrTime = ah + am/60;
        let depTime = dh + dm/60;
        let worked = depTime - arrTime;
        
        let isLate = false;
        let isEarly = false;
        let ot = 0.0;
        
        if (isSunday) {
            ot = Math.max(0, worked);
        } else if (isSaturday) {
            if (arrTime > 8.0) isLate = true;
            if (depTime < 13.0) isEarly = true;
            if (depTime > 13.0) ot = depTime - 13.0;
        } else {
            if (arrTime > 8.0) isLate = true;
            if (depTime < 17.0) isEarly = true;
            if (depTime > 17.0) ot = depTime - 17.0;
        }
        
        if (lateCheck) lateCheck.checked = isLate;
        if (earlyCheck) earlyCheck.checked = isEarly;
        if (otDisplay) otDisplay.textContent = ot.toFixed(2);
    } else {
        if (lateCheck) lateCheck.checked = false;
        if (earlyCheck) earlyCheck.checked = false;
        if (otDisplay) otDisplay.textContent = '0.00';
    }
}"""

if old_script in content:
    content = content.replace(old_script, new_script)
    with open('templates/attendance.html', 'w') as f:
        f.write(content)
        print("Success frontend")
else:
    print("Could not find old script")
