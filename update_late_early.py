import re

with open('templates/attendance.html', 'r') as f:
    content = f.read()

# 1. Replace the checkbox inputs with spans
late_old = """<input type="checkbox" name="day_{{ day.date.day }}_late" onclick="return false;" {% if day.late_arrival %}checked{% endif %} class="rounded text-[#2F6F63] focus:ring-[#2F6F63]" {% if g.user and g.user.role == "Finance" %}disabled{% endif %} >"""
late_new = """<span id="late_display_{{ day.date.day }}" class="text-[#B3432B] font-medium">-</span>"""
content = content.replace(late_old, late_new)
# Fallback in case the exact string wasn't matched due to spacing
content = re.sub(r'<input type="checkbox" name="day_\{\{ day\.date\.day \}\}_late".*?>', late_new, content)

early_old = """<input type="checkbox" name="day_{{ day.date.day }}_early" onclick="return false;" {% if day.early_departure %}checked{% endif %} class="rounded text-[#2F6F63] focus:ring-[#2F6F63]" {% if g.user and g.user.role == "Finance" %}disabled{% endif %} >"""
early_new = """<span id="early_display_{{ day.date.day }}" class="text-[#B3432B] font-medium">-</span>"""
content = content.replace(early_old, early_new)
content = re.sub(r'<input type="checkbox" name="day_\{\{ day\.date\.day \}\}_early".*?>', early_new, content)


# 2. Update the javascript
script_old = """<script>
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

script_new = """<script>
function formatDuration(hoursDecimal) {
    if (hoursDecimal <= 0) return "-";
    const h = Math.floor(hoursDecimal);
    const m = Math.round((hoursDecimal - h) * 60);
    if (h > 0 && m > 0) return `${h}h ${m}m`;
    if (h > 0) return `${h}h`;
    return `${m}m`;
}

function calcOT(dayNum, isSunday, isSaturday) {
    const arrInput = document.querySelector(`[name="day_${dayNum}_arrival"]`);
    const depInput = document.querySelector(`[name="day_${dayNum}_departure"]`);
    const lateSpan = document.getElementById(`late_display_${dayNum}`);
    const earlySpan = document.getElementById(`early_display_${dayNum}`);
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
        
        let lateHours = 0;
        let earlyHours = 0;
        let ot = 0.0;
        
        if (isSunday) {
            ot = Math.max(0, worked);
        } else if (isSaturday) {
            if (arrTime > 8.0) lateHours = arrTime - 8.0;
            if (depTime < 13.0) earlyHours = 13.0 - depTime;
            if (depTime > 13.0) ot = depTime - 13.0;
        } else {
            if (arrTime > 8.0) lateHours = arrTime - 8.0;
            if (depTime < 17.0) earlyHours = 17.0 - depTime;
            if (depTime > 17.0) ot = depTime - 17.0;
        }
        
        if (lateSpan) lateSpan.textContent = formatDuration(lateHours);
        if (earlySpan) earlySpan.textContent = formatDuration(earlyHours);
        if (otDisplay) otDisplay.textContent = ot.toFixed(2);
    } else {
        if (lateSpan) lateSpan.textContent = "-";
        if (earlySpan) earlySpan.textContent = "-";
        if (otDisplay) otDisplay.textContent = '0.00';
    }
}

document.addEventListener("DOMContentLoaded", function() {
    {% for day in days %}
    calcOT({{ day.date.day }}, {{ 'true' if day.is_sunday else 'false' }}, {{ 'true' if day.date.weekday() == 5 else 'false' }});
    {% endfor %}
});"""

if script_old in content:
    content = content.replace(script_old, script_new)
    with open('templates/attendance.html', 'w') as f:
        f.write(content)
        print("Success UI Update")
else:
    print("Failed to find old script block.")

