# Make Hard-Coded Lists Editable in System Settings

Currently, the application relies on several hard-coded lists (Departments, Employment Types, Employment Statuses, Social Statuses, and Genders). This plan makes these lists user-editable via the System Settings interface.

## Proposed Changes

### Backend (`app.py`)
- Remove the hard-coded global variables for `DEPARTMENTS`, `EMPLOYMENT_TYPES`, `EMPLOYMENT_STATUSES`, `TAX_FILING_STATUSES`, and `GENDERS`.
- Introduce a helper function `get_list_setting(key, default_list)` to fetch and parse comma-separated lists from the `company_settings` database table.
- Modify the `company_settings` POST route to accept, validate, and save these new lists as comma-separated strings.
- Pass these dynamic lists into `render_template` for `list_employees`, `add_employee`, and `edit_employee`.

### System Settings UI (`templates/settings.html`)
- Add a new "Dropdown Lists & Categories" section to the settings form.
- Add text inputs (or textareas) for:
  - Departments
  - Employment Types
  - Employment Statuses
  - Social Statuses
  - Genders
- Provide instructional text explaining that users should enter values separated by commas (e.g., "HR, IT, Sales").

## Open Questions & Limitations
> [!WARNING]
> I have intentionally **excluded** `Employee Categories` (Employee vs Labourer), `Payment Methods` (Bank Transfer), `Attendance Statuses` (Present/Absent/Half-day), and `Leave Types` from being editable. 
> 
> The core system logic (specifically the **Payroll Calculation Engine** and **Attendance Logic**) contains deep, hard-coded mathematical rules that rely precisely on those exact words to function. Allowing users to rename or delete those would immediately break payroll generation and attendance tracking. 

## Verification Plan
1. Open the System Settings page and verify the new fields appear with their default values.
2. Edit the "Departments" list, save it, and verify the changes persist.
3. Open the "Add Employee" screen and confirm the "Department" dropdown reflects the updated list.
