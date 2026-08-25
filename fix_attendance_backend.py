import re

with open('app.py', 'r') as f:
    content = f.read()

# Replace lines inside save_attendance
old_logic = """                late = request.form.get(f"{prefix}late_arrival") == "on"
                early = request.form.get(f"{prefix}early_departure") == "on"
                notes = request.form.get(f"{prefix}notes", "").strip() or None
                is_sunday = dt.weekday() == 6

                # Calculate OT from arrival/departure
                ot_hours = 0.0
                ot_hours_sunday = 0.0
                if arrival and departure and status == "Present":
                    try:
                        arr = datetime.strptime(arrival, "%H:%M")
                        dep = datetime.strptime(departure, "%H:%M")
                        worked = (dep - arr).total_seconds() / 3600
                        if worked > 8:
                            excess = round(worked - 8, 2)
                            if is_sunday:
                                ot_hours_sunday = excess
                            else:
                                ot_hours = excess
                    except ValueError:
                        pass

                # If Sunday and Present, the whole day counts as Sunday work
                # (for OT calc purposes, the first 8 hours are double rate, beyond is triple)
                if is_sunday and arrival and departure and status == "Present":
                    try:
                        arr = datetime.strptime(arrival, "%H:%M")
                        dep = datetime.strptime(departure, "%H:%M")
                        total_worked = max(0, (dep - arr).total_seconds() / 3600)
                        ot_hours_sunday = round(total_worked, 2)
                        ot_hours = 0  # All Sunday hours go to sunday column
                    except ValueError:
                        pass"""

new_logic = """                notes = request.form.get(f"{prefix}notes", "").strip() or None
                is_sunday = dt.weekday() == 6
                
                late = False
                early = False
                ot_hours = 0.0
                ot_hours_sunday = 0.0
                
                if arrival and departure and status == "Present":
                    try:
                        from datetime import datetime
                        arr = datetime.strptime(arrival, "%H:%M")
                        dep = datetime.strptime(departure, "%H:%M")
                        arr_time = arr.time()
                        dep_time = dep.time()
                        
                        standard_start = datetime.strptime("08:00", "%H:%M").time()
                        
                        if is_sunday:
                            total_worked = max(0, (dep - arr).total_seconds() / 3600)
                            ot_hours_sunday = round(total_worked, 2)
                        elif dt.weekday() == 5:
                            # Saturday (Half Day)
                            standard_end_sat = datetime.strptime("13:00", "%H:%M").time()
                            if arr_time > standard_start: late = True
                            if dep_time < standard_end_sat: early = True
                            if dep_time > standard_end_sat:
                                ot_dt = datetime.strptime("13:00", "%H:%M")
                                ot_hours = round(max(0, (dep - ot_dt).total_seconds() / 3600), 2)
                        else:
                            # Weekday
                            standard_end = datetime.strptime("17:00", "%H:%M").time()
                            if arr_time > standard_start: late = True
                            if dep_time < standard_end: early = True
                            if dep_time > standard_end:
                                ot_dt = datetime.strptime("17:00", "%H:%M")
                                ot_hours = round(max(0, (dep - ot_dt).total_seconds() / 3600), 2)
                    except ValueError:
                        pass"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    with open('app.py', 'w') as f:
        f.write(content)
        print("Success app.py")
else:
    print("Could not find old logic in app.py")

