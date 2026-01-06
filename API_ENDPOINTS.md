# Isuku App - API Endpoints Reference

## Base URL
Assuming the server is running on `http://localhost:8080` or `http://0.0.0.0:8080`

---

## 📄 **Page URLs (Web Pages)**

### Landing & Registration
- **Landing Page**: `http://localhost:8080/`
- **Registration Selection**: `http://localhost:8080/register/`
- **Set Language**: `http://localhost:8080/set-language/` (POST)
- **Contact Form**: `http://localhost:8080/contact/` (POST)

### Household
- **Household Signup**: `http://localhost:8080/household/signup/`
- **Household Login**: `http://localhost:8080/household/login/`
- **Household Dashboard**: `http://localhost:8080/household/dashboard/`

### Collector
- **Collector Signup**: `http://localhost:8080/collector/signup/`
- **Collector Login**: `http://localhost:8080/collector/login/`
- **Collector Dashboard**: `http://localhost:8080/collector/dashboard/`

### Admin
- **Admin Login**: `http://localhost:8080/admin/login/`
- **Admin Dashboard**: `http://localhost:8080/portal-admin/dashboard/`
- **Django Admin**: `http://localhost:8080/admin/`

### Utility
- **Logout**: `http://localhost:8080/logout/`

---

## 🔌 **API Endpoints (JSON)**

### Location APIs (Cascading Dropdowns)

#### 1. Get Districts
- **URL**: `http://localhost:8080/api/districts/`
- **Method**: `GET` or `POST`
- **Parameters**: 
  ```json
  {
    "province": "Kigali"  // Optional: filter by province
  }
  ```
- **Response**:
  ```json
  {
    "districts": [
      {"id": 1, "name": "Gasabo"},
      {"id": 2, "name": "Kicukiro"},
      ...
    ]
  }
  ```

#### 2. Get Sectors
- **URL**: `http://localhost:8080/api/sectors/`
- **Method**: `GET` or `POST`
- **Parameters**:
  ```json
  {
    "district": "Gasabo"  // Required: district name
  }
  ```
- **Response**:
  ```json
  {
    "sectors": [
      {"id": 1, "name": "Gisozi"},
      {"id": 2, "name": "Kimisagara"},
      ...
    ]
  }
  ```

#### 3. Get Cells
- **URL**: `http://localhost:8080/api/cells/`
- **Method**: `GET` or `POST`
- **Parameters**:
  ```json
  {
    "sector": "Gisozi"  // Required: sector name
  }
  ```
- **Response**:
  ```json
  {
    "cells": [
      {"id": 1, "name": "Cell 1"},
      {"id": 2, "name": "Cell 2"},
      ...
    ]
  }
  ```

#### 4. Get Villages
- **URL**: `http://localhost:8080/api/villages/`
- **Method**: `GET` or `POST`
- **Parameters**:
  ```json
  {
    "cell": "Cell 1"  // Required: cell name
  }
  ```
- **Response**:
  ```json
  {
    "villages": [
      {"id": 1, "name": "Village 1"},
      {"id": 2, "name": "Village 2"},
      ...
    ]
  }
  ```

---

### OTP APIs

#### 1. Request OTP
- **URL**: `http://localhost:8080/api/request-otp/` or `http://localhost:8080/api/send-otp/`
- **Method**: `POST`
- **Content-Type**: `application/json` or `application/x-www-form-urlencoded`
- **Parameters**:
  ```json
  {
    "phoneNumber": "+250788123456"  // or "phone_number"
  }
  ```
- **Response**:
  ```json
  {
    "message": "OTP sent",
    "otp": "123456",  // 6-digit code (for development)
    "success": true
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "Phone number is required",
    "success": false
  }
  ```

#### 2. Verify OTP
- **URL**: `http://localhost:8080/api/verify-otp/`
- **Method**: `POST`
- **Content-Type**: `application/json` or `application/x-www-form-urlencoded`
- **Parameters**:
  ```json
  {
    "otp": "123456"  // or "otp_code"
  }
  ```
- **Response**:
  ```json
  {
    "message": "OTP verified successfully",
    "success": true
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "Invalid or expired OTP",
    "success": false
  }
  ```

#### 3. Resend OTP
- **URL**: `http://localhost:8080/api/resend-otp/`
- **Method**: `POST`
- **Content-Type**: `application/json` or `application/x-www-form-urlencoded`
- **Parameters**:
  ```json
  {
    "phoneNumber": "+250788123456"  // or "phone_number"
  }
  ```
- **Response**:
  ```json
  {
    "message": "OTP resent",
    "otp": "654321",  // New 6-digit code (for development)
    "success": true
  }
  ```

---

### Pickup Request APIs

#### 1. Create Pickup Request
- **URL**: `http://localhost:8080/pickup/create/`
- **Method**: `POST`
- **Content-Type**: `application/x-www-form-urlencoded` or `multipart/form-data`
- **Parameters**: (Form data)
  - `household`: Household ID
  - `waste_type`: Type of waste
  - `quantity`: Quantity
  - `pickup_date`: Preferred pickup date
  - `address`: Pickup address
  - `notes`: Additional notes (optional)

#### 2. Assign Pickup
- **URL**: `http://localhost:8080/pickup/<pickup_id>/assign/`
- **Method**: `POST`
- **Parameters**: (Form data)
  - `collector`: Collector ID
  - `pickup_id`: Pickup request ID (in URL)

---

## 🔐 **Authentication**

### Login Endpoints
All login endpoints accept `POST` requests with form data:
- `username` or `email`
- `password`

### Signup Endpoints
All signup endpoints accept `POST` requests with form data:
- Household/Collector specific fields
- Phone number (for OTP verification)
- Location fields (province, district, sector, cell, village)

---

## 📝 **Testing the APIs**

### Using cURL

#### Request OTP:
```bash
curl -X POST http://localhost:8080/api/request-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+250788123456"}'
```

#### Verify OTP:
```bash
curl -X POST http://localhost:8080/api/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"otp": "123456"}'
```

#### Get Districts:
```bash
curl -X POST http://localhost:8080/api/districts/ \
  -H "Content-Type: application/json" \
  -d '{"province": "Kigali"}'
```

### Using Python (requests library)
```python
import requests

# Request OTP
response = requests.post(
    'http://localhost:8080/api/request-otp/',
    json={'phoneNumber': '+250788123456'}
)
print(response.json())

# Verify OTP
response = requests.post(
    'http://localhost:8080/api/verify-otp/',
    json={'otp': '123456'}
)
print(response.json())
```

### Using JavaScript (fetch)
```javascript
// Request OTP
fetch('http://localhost:8080/api/request-otp/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        phoneNumber: '+250788123456'
    })
})
.then(response => response.json())
.then(data => console.log(data));

// Verify OTP
fetch('http://localhost:8080/api/verify-otp/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        otp: '123456'
    })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 🎯 **Quick Access Links**

Once your server is running, you can access:

1. **Landing Page**: http://localhost:8080/
2. **Household Dashboard**: http://localhost:8080/household/dashboard/
3. **Collector Dashboard**: http://localhost:8080/collector/dashboard/
4. **Admin Dashboard**: http://localhost:8080/portal-admin/dashboard/
5. **Django Admin**: http://localhost:8080/admin/

---

## ⚠️ **Notes**

- All API endpoints require CSRF token for POST requests (except those marked with `@csrf_exempt`)
- OTP endpoints are currently `@csrf_exempt` for easier testing
- OTP codes expire after 10 minutes
- Location APIs return data based on Rwanda's administrative divisions
- The server port may vary (check your `runserver` command)

