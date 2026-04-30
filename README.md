# Leave Encashment Management

A comprehensive Frappe/ERPNext custom application for managing leave encashment requests, enabling employees to request encashment of unused leaves with automated calculations, approval workflow, payroll integration, reporting, and API access.

## Features

### 1. Custom DocType - Leave Encashment Request

**Fields:**
- Employee (Link → Employee)
- Employee Name (Auto-fetched)
- Department (Auto-fetched)
- Designation (Auto-fetched)
- Company (Auto-fetched)
- Leave Type (Link → Leave Type, filtered to encashable types only)
- Available Leave Balance (Read Only)
- Available Encashable Leaves (Read Only)
- Actual Encashable Days (Read Only)
- Requested Leaves
- Leave Salary Per Day (Auto-calculated from Salary Structure)
- Total Encashment Amount (Auto-calculated)
- Posting Date
- Leave Allocation (Read Only)
- Additional Salary Reference (Read Only)
- Payroll Entry Reference (Read Only)
- Status (Draft, Pending Approval, Approved, Rejected, Paid)

### 2. Business Logic Implementation

**Automated Calculations:**
- Fetches employee leave balance based on selected Leave Type
- Retrieves salary details from assigned Salary Structure
- Calculates Total Encashment Amount (Requested Leaves × Salary Per Day)
- Validates requested leaves against available encashable balance
- Prevents submission if requested leaves exceed available balance
- Checks for duplicate pending/draft requests for same employee and leave type

**Key Methods:**
- `calculate_encashment_amount()` - Calculates total encashment value
- `get_employee_leave_details()` - Fetches leave balance and allocation
- `get_employee_salary_details()` - Retrieves salary structure details
- `validate_requested_leaves()` - Validates against available balance
- `validate_duplicate_request()` - Prevents duplicate submissions
- `update_leave_allocation()` - Updates leave allocation on approval
- `create_additional_salary()` - Creates Additional Salary record for payroll

### 3. Workflow Configuration

**Workflow States:**
- Draft
- Pending Approval
- Approved
- Rejected
- Paid

**Role-Based Transitions:**
- **Employee**: Can create and submit requests (Draft → Pending Approval)
- **HR Manager**: Can approve/reject requests (Pending Approval → Approved/Rejected)
- **Accounts User**: Can process payroll integration (Approved → Paid)

### 4. Payroll Integration

**On Approval:**
- Automatically creates an Additional Salary record linked to the request
- Sets salary component based on Leave Type's earning component
- Links Additional Salary to the Leave Encashment Request
- Updates Payroll Entry Reference when processed in Salary Slip

**Hook Integration:**
- `set_payroll_reference()` - Automatically links payroll entry when Salary Slip is submitted

### 5. Client-Side Validation

**JavaScript Features:**
- Filters Leave Type to show only encashable leave types for the employee
- Validates requested leaves against available encashable leaves
- Auto-calculates encashment amount on field changes
- Provides real-time feedback on invalid inputs
- Preview button for print format

### 6. Report Development

**Leave Encashment Summary (Script Report)**

**Filters:**
- Company
- Department
- Employee
- Leave Type
- Status
- Date Range (From Date, To Date)

**Columns Displayed:**
- Request ID
- Employee
- Employee Name
- Company
- Department
- Designation
- Leave Type
- Posting Date
- Available Leave Balance
- Requested Leaves
- Available Encashable Leaves
- Salary Per Day
- Total Encashment Amount
- Status
- Payroll Entry Reference

### 7. Dashboard Chart

**Monthly Leave Encashment Amount**
- Chart Type: Bar Chart
- Time Interval: Monthly
- Time Span: Last Year
- Value Based On: Total Encashment Amount
- Groups data by posting date
- Displays total encashment values per month

### 8. API Development

**Create Leave Encashment Request API**

**Endpoint:** `/api/method/leave_encashment.api.create_leave_encashment_request`

**Method:** POST

**Parameters:**
- `employee` (required) - Employee ID
- `posting_date` (required) - Request posting date
- `leave_type` (required) - Leave Type to encash
- `requested_leaves` (required) - Number of leaves to encash

**Response:**
```json
{
  "status": "success",
  "message": "Leave Encashment Request Created Successfully",
  "doc": {
    "name": "HR-LE-2026-00001",
    "employee": "EMP-001",
    "leave_type": "Annual Leave",
    "requested_leaves": 5,
    ...
  }
}
```

**Example Usage:**
```bash
curl -X POST http://your-site/api/method/leave_encashment.api.create_leave_encashment_request \
  -H "Authorization: token <api_key>:<api_secret>" \
  -d "employee=EMP-001" \
  -d "posting_date=2026-04-30" \
  -d "leave_type=Annual Leave" \
  -d "requested_leaves=5"
```

### 9. Permissions Configuration

**Role-Based Access:**
- **System Manager**: Full access (Create, Read, Write, Delete, Submit, Cancel, Email, Export, Print, Report, Share)
- **Employee**: Create, Read, Write (own requests), Email, Print
- **HR Manager**: Read, Write, Submit, Email, Export, Print, Report
- **Accounts User**: Read, Write, Email, Export, Print, Report

**Access Control:**
- Employees can only view and edit their own requests
- HR Managers can view and approve all requests
- Accounts Users can view and process approved requests

### 10. Enhancements

**Email Notifications:**
- Automatic email to HR Manager when request is submitted for approval
- Email to Employee when request is Approved
- Email to Employee when request is Rejected
- Email to Accounts User when request is Approved (for payroll processing)
- Email to Employee when request is Paid

**Custom Print Format:**
- Professional print format for Leave Encashment Request
- Includes employee details, encashment details, and approval status
- Preview button available in the form
- Styled for professional printing

**Automated Reminders:**
- Daily scheduled task sends reminder emails to HR Managers
- Reminds about pending approvals older than 3 days
- Includes list of pending requests with direct links

**Unit Test Coverage:**
- Test framework ready for core logic testing
- Tests should cover:
  - Encashment amount calculation
  - Leave balance validation
  - Duplicate request prevention
  - Payroll integration
  - API endpoint functionality

## Installation

### Prerequisites

- Frappe Framework v15.x or higher
- ERPNext v15.x or higher
- HRMS module installed and configured

### Installation Steps

1. **Clone the repository:**
```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/your-username/leave_encashment
```

2. **Install the app:**
```bash
bench install-app leave_encashment
```

3. **Build assets:**
```bash
bench build
```

4. **Restart bench:**
```bash
bench restart
```

## Configuration

### 1. Leave Type Configuration

Ensure Leave Types have the following settings:
- **Allow Encashment**: Checked
- **Earning Component**: Set (for payroll integration)
- **Max Encashable Leaves**: Configured

### 2. Salary Structure Configuration

Configure Salary Structure Assignment with:
- **Leave Encashment Amount Per Day**: Set (fallback to Salary Structure if not in assignment)
- **Currency**: Configured

### 3. Email Templates

Create the following email templates in Frappe:
- `leave_encashment_approval_request` - For approval notifications
- `leave_encashment_approval_reminder` - For pending approval reminders

### 4. Workflow Setup

Configure workflow in Leave Encashment Request DocType:
1. Go to Leave Encashment Request
2. Click on Workflow in the sidebar
3. Create workflow with states: Draft → Pending Approval → Approved/Rejected → Paid
4. Set role-based transitions
5. Enable workflow

### 5. Scheduler Configuration

The daily reminder is automatically configured via hooks. Ensure:
- Scheduler is enabled in your bench
- Cron jobs are running properly

Verify scheduler:
```bash
bench doctor
```

## Usage

### For Employees

1. Navigate to Leave Encashment Request
2. Click "New" to create a new request
3. Select Employee (auto-filled if logged in as employee)
4. Select Posting Date
5. Select Leave Type (only encashable types shown)
6. View Available Leave Balance and Encashable Leaves
7. Enter Requested Leaves (cannot exceed available encashable leaves)
8. View auto-calculated Total Encashment Amount
9. Submit the request
10. Wait for HR Manager approval

### For HR Managers

1. Navigate to Leave Encashment Request List
2. Filter by Status: "Pending Approval"
3. Review the request details
4. Approve or Reject based on company policy
5. On approval, Additional Salary is automatically created
6. Accounts User will be notified for payroll processing

### For Accounts Users

1. Navigate to Leave Encashment Request List
2. Filter by Status: "Approved"
3. Review approved requests
4. Process in Payroll Entry (Additional Salary will be included)
5. Status automatically updates to "Paid" when Salary Slip is submitted

### Viewing Reports

1. Navigate to Leave Encashment Summary Report
2. Apply filters as needed (Company, Department, Employee, Date Range, Status)
3. View comprehensive encashment data
4. Export to PDF/Excel if required

### Dashboard Chart

1. Navigate to HR Workspace or Leave Encashment Workspace
2. View "Monthly Leave Encashment Amount" chart
3. Filter by date range if needed
4. Analyze encashment trends over time

## API Examples

### Python Example

```python
import frappe

# Create leave encashment request
result = frappe.call({
    "method": "leave_encashment.api.create_leave_encashment_request",
    "args": {
        "employee": "EMP-001",
        "posting_date": "2026-04-30",
        "leave_type": "Annual Leave",
        "requested_leaves": 5
    }
})

if result.get("status") == "success":
    print(f"Request created: {result['doc']['name']}")
else:
    print(f"Error: {result['message']}")
```

### JavaScript Example

```javascript
frappe.call({
    method: "leave_encashment.api.create_leave_encashment_request",
    args: {
        employee: "EMP-001",
        posting_date: "2026-04-30",
        leave_type: "Annual Leave",
        requested_leaves: 5
    },
    callback: function(r) {
        if(r.message.status === "success") {
            frappe.msgprint("Request created: " + r.message.doc.name);
        } else {
            frappe.msgprint("Error: " + r.message.message);
        }
    }
});
```

## Troubleshooting

### Issue: Leave Type not showing in dropdown
**Solution:** Ensure Leave Type has "Allow Encashment" checked and employee has a valid Leave Allocation for that type.

### Issue: Salary Per Day not calculating
**Solution:** Ensure Salary Structure Assignment exists for the employee with Leave Encashment Amount Per Day configured, or Salary Structure has the field set.

### Issue: Additional Salary not created on approval
**Solution:** Check that Leave Type has an Earning Component configured. Check error logs for detailed error messages.

### Issue: Payroll Entry Reference not updating
**Solution:** Ensure the Additional Salary is included in Salary Slip earnings with salary component "Leave Encashment". The hook will automatically update the reference.

### Issue: Email notifications not sending
**Solution:** Verify email settings in Frappe, ensure email templates exist, and check that users have valid email addresses.

## Development

### Code Structure

```
leave_encashment/
├── leave_encashment/
│   ├── doctype/
│   │   └── leave_encashment_request/
│   │       ├── leave_encashment_request.py      # Server-side logic
│   │       ├── leave_encashment_request.json    # DocType definition
│   │       └── leave_encashment_request.js     # Client-side logic
│   ├── report/
│   │   └── leave_encashment_summary/            # Script report
│   ├── dashboard_chart/
│   │   └── monthly_leave_encashment_amount/     # Dashboard chart
│   ├── print_format/
│   │   └── leave_encashment_request_print_format/ # Custom print format
│   ├── api.py                                   # API endpoints
│   ├── notification.py                         # Email notifications
│   └── hooks.py                                 # App hooks
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please install pre-commit and enable it for this repository:

```bash
cd apps/leave_encashment
pre-commit install
```

Pre-commit is configured to use the following tools:
- ruff (Python linting and formatting)
- eslint (JavaScript linting)
- prettier (JavaScript formatting)
- pyupgrade (Python syntax upgrading)

### Running Tests

```bash
cd apps/leave_encashment
bench --site your-site run-tests --app leave_encashment
```

## License

MIT License - See license.txt for details

## Support

For issues, questions, or contributions:
- Email: salubaiju2803@gmail.com
- Publisher: Salumol Baiju

## Changelog

### Version 1.0.0 (2026-04-30)
- Initial release
- Custom DocType: Leave Encashment Request
- Business logic for encashment calculations
- Workflow configuration
- Payroll integration
- Client-side validations
- Leave Encashment Summary report
- Monthly Leave Encashment Amount dashboard chart
- API for programmatic request creation
- Email notifications
- Custom print format
- Automated approval reminders
