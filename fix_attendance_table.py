import re

with open('templates/payslip_pdf.html', 'r') as f:
    content = f.read()

# Replace the attendance summary table
old_table = """    <table class="summary-table">
        <tr>
            <th style="width: 20%;">Working Days</th>
            <td style="width: 13%;">{{ payslip.working_days or 0 }}</td>
            <th style="width: 20%;">Late Arrivals</th>
            <td style="width: 13%;">{{ payslip.late_arrivals or 0 }}</td>
            <th style="width: 20%;">Annual Leave</th>
            <td style="width: 14%;">{{ payslip.annual_leave_taken or 0 }}</td>
        </tr>
        <tr>
            <th>Absences</th>
            <td>{{ payslip.absences or 0 }}</td>
            <th>Early Departures</th>
            <td>{{ payslip.early_departures or 0 }}</td>
            <th>Casual Leave</th>
            <td>{{ payslip.casual_leave_taken or 0 }}</td>
        </tr>
        <tr>
            <th>No-Pay Days</th>
            <td>{{ payslip.no_pay_days or 0 }}</td>
            <th></th>
            <td></td>
            <th>Medical Leave</th>
            <td>{{ payslip.medical_leave_taken or 0 }}</td>
        </tr>
    </table>"""

new_table = """    <table class="summary-table" style="width:100%;">
        <tr>
            <th style="width: 15%;">Work Days</th>
            <td style="width: 10%;">{{ payslip.working_days or 0 }}</td>
            <th style="width: 15%;">Absences</th>
            <td style="width: 10%;">{{ payslip.absences or 0 }}</td>
            <th style="width: 15%;">Late Arr.</th>
            <td style="width: 10%;">{{ payslip.late_arrivals or 0 }}</td>
            <th style="width: 15%;">Early Dep.</th>
            <td style="width: 10%;">{{ payslip.early_departures or 0 }}</td>
        </tr>
        <tr>
            <th>No-Pay</th>
            <td>{{ payslip.no_pay_days or 0 }}</td>
            <th>Annual L.</th>
            <td>{{ payslip.annual_leave_taken or 0 }}</td>
            <th>Casual L.</th>
            <td>{{ payslip.casual_leave_taken or 0 }}</td>
            <th>Medical L.</th>
            <td>{{ payslip.medical_leave_taken or 0 }}</td>
        </tr>
    </table>"""

content = content.replace(old_table, new_table)
content = content.replace('<br><br>', '<br>')

with open('templates/payslip_pdf.html', 'w') as f:
    f.write(content)

