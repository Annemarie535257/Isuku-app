# Setup Guide: OTP Verification and Rwanda Administrative Data

## Overview
This guide explains how to set up OTP verification for phone numbers and load Rwanda's administrative divisions data (Provinces, Districts, Sectors, Cells, Villages).

## Features Implemented

### 1. OTP Verification System
- Phone number verification using OTP (One-Time Password)
- OTP codes displayed in modal for user entry
- OTP expiration (10 minutes)
- OTP verification for registration

### 2. Rwanda Administrative Data
- Complete administrative structure: Provinces → Districts → Sectors → Cells → Villages
- Cascading dropdowns with AJAX
- Dynamic loading of administrative divisions based on user selection

## Setup Instructions

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- Django>=4.2.0
- Jinja2>=3.1.0

### Step 2: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Load Rwanda Administrative Data
```bash
python manage.py load_rwanda_data
```

This command will load all provinces, districts, sectors, cells, and villages from the data file.

### Step 4: Run the Server
```bash
python manage.py runserver 8080
```

## How It Works

### Registration Flow with OTP
1. User fills out the registration form
2. User clicks "Verify Phone Number" button
3. System generates OTP and displays it in a modal
4. User enters the OTP code from the modal
5. System verifies the OTP
6. User completes and submits the form
7. Account is created with verified phone number

### Cascading Dropdowns
1. User selects a Province
2. Districts for that province are loaded via AJAX
3. User selects a District
4. Sectors for that district are loaded via AJAX
5. User selects a Sector
6. Cells for that sector are loaded via AJAX
7. User selects a Cell
8. Villages for that cell are loaded via AJAX

## API Endpoints

### Administrative Data Endpoints
- `GET /api/districts/?province_id=<id>` - Get districts for a province
- `GET /api/sectors/?district_id=<id>` - Get sectors for a district
- `GET /api/cells/?sector_id=<id>` - Get cells for a sector
- `GET /api/villages/?cell_id=<id>` - Get villages for a cell

### OTP Endpoints
- `POST /api/send-otp/` - Send OTP to phone number
  ```json
  {
    "phone_number": "+250788888888",
    "purpose": "registration"
  }
  ```
  
- `POST /api/verify-otp/` - Verify OTP code
  ```json
  {
    "phone_number": "+250788888888",
    "otp_code": "123456",
    "purpose": "registration"
  }
  ```

## Testing

### Testing OTP
1. Start the server
2. Go to the registration page
3. Enter a phone number
4. Click "Verify Phone Number"
5. OTP code will be displayed in the modal
6. Enter the OTP code in the modal
7. Complete registration

### Testing Cascading Dropdowns
1. Go to the registration page
2. Select a province from the dropdown
3. Districts should load automatically
4. Select a district
5. Sectors should load automatically
6. Continue selecting down the hierarchy

## Troubleshooting

### OTP Not Working
- Check that OTP modal is displaying correctly
- Verify phone number format (should start with +250 for Rwanda)
- Ensure OTP code is entered correctly (6 digits)

### Cascading Dropdowns Not Working
- Check browser console for errors
- Verify that Rwanda data is loaded: `python manage.py load_rwanda_data`
- Check that AJAX endpoints are accessible

### Migration Errors
- Make sure you're in the virtual environment
- Run `python manage.py makemigrations` first
- Then run `python manage.py migrate`

## Production Considerations

1. **SMS Integration**: Consider integrating an SMS service provider for production OTP delivery
2. **Security**: Implement rate limiting to OTP endpoints to prevent abuse
3. **Data Validation**: Ensure phone numbers are validated before sending OTP
4. **Error Handling**: Add proper error handling and logging

## File Structure

```
registration/
├── models.py              # OTP model
├── views.py               # API endpoints and views
├── data/
│   └── rwanda_admin_data.py  # Rwanda administrative data
└── management/
    └── commands/
        └── load_rwanda_data.py  # Management command to load data
```

## Next Steps

1. Add OTP verification to collector registration
2. Add OTP verification to login process
3. Add password reset with OTP
4. Expand Rwanda administrative data with more complete village data
5. Add caching for administrative data queries
6. Add unit tests for OTP service

