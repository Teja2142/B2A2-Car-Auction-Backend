## User Profile Management (Industry Standard)

### Admin CRUD
- Admins can create, update, delete, and list any user via `/users/accounts/` endpoints (admin only).

### Self-Service Profile (Dealers/Customers)
- Authenticated users can view and update their own profile via:
	- `GET    /api/users/profile/`   (view your profile)
	- `PUT    /api/users/profile/`   (update all fields)
	- `PATCH  /api/users/profile/`   (update some fields)
- No admin needed for these actions.
- Users cannot set staff/superuser fields or update other users.

### Why?
- This matches real-world car auction and e-commerce platforms.
- Improves user experience and security.

### Example Usage
1. Login and get your JWT token.
2. Use `/api/users/profile/` with your token to view or update your info.

### API Docs
- All endpoints are documented in Swagger UI (`/api/docs/`).
# 🚗 B2A2 Car Auction Backend

Backend for **B2A2 Car Auction** – Django REST API for vehicles, auctions, bids, and unified user accounts (regular users, dealers, admins) with form-based Swagger docs.

---

## 📚 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features
- Unified User model with `user_type` (dealer / customer / admin)
- Registration, login, password reset (form inputs)
- JWT authentication (SimpleJWT) & admin/staff creation via API
- CRUD for vehicles (with images), auctions, bids
- Bulk vehicle image upload endpoint
- Dealer ownership rules: only creating dealer can update/delete their vehicles
- Swagger docs render HTML forms (no raw JSON bodies for POST/PUT/PATCH)
- Validation: unique email/mobile, VIN regex, year/mileage bounds, password complexity
- Safe swagger parameter generation avoiding migration-time DB errors

---

## 🛠 Tech Stack
- **Backend:** Django, Django REST Framework
- **Database:** SQLite (default), easy to switch to PostgreSQL/MySQL
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Other:** CORS, CSRF protection, Mailgun/Gmail for emails

---

## 🚀 Getting Started

### 1. Clone the repository
```sh
git clone https://github.com/yourusername/B2A2-Car-Auction-Backend.git
cd B2A2-Car-Auction-Backend
```

### 2. Create and activate a virtual environment
```sh
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Mac/Linux
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file or set the following in your environment:
```env
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
PSWD_RESET_BASE_LINK=http://127.0.0.1:8000/api/password-reset
```

### 5. Run migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser
```sh
python manage.py createsuperuser
```

### 7. Start the development server
```sh
python manage.py runserver
```

---

## 📡 API Overview

### Auth & Accounts
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/users/accounts/` | GET | Admin | List users |
| `/api/users/accounts/` | POST | Admin | Create user (set `is_staff`/`is_superuser`) |
| `/api/users/accounts/{id}/` | GET | Admin | Retrieve user |
| `/api/users/accounts/{id}/` | PUT | Admin | Full update (all required) |
| `/api/users/accounts/{id}/` | PATCH | Admin | Partial update (optional fields) |
| `/api/users/accounts/{id}/` | DELETE | Admin | Delete user |
| `/api/users/login/` | POST | Public | Obtain JWT |
| `/api/users/register/` | POST | Public | Register new user |
| `/api/users/password-reset/` | POST | Public | Request password reset |
| `/api/users/password-reset/<token>/` | POST | Public | Confirm password reset |

### Vehicles
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/vehicles/` | GET | Public | List vehicles (search/filter/order) |
| `/api/vehicles/` | POST | Auth (dealer) | Create vehicle |
| `/api/vehicles/{id}/` | GET | Public | Retrieve vehicle |
| `/api/vehicles/{id}/` | PUT | Auth (owning dealer) | Full update |
| `/api/vehicles/{id}/` | PATCH | Auth (owning dealer) | Partial update |
| `/api/vehicles/{id}/` | DELETE | Auth (owning dealer) | Delete vehicle |
| `/api/vehicle-images/` | POST | Auth | Upload single image |
| `/api/vehicle-images/bulk-upload/` | POST | Auth | Bulk upload images |

### Auctions
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auction/auctions/` | GET | Public | List auctions |
| `/api/auction/auctions/` | POST | Auth | Create auction |
| `/api/auction/auctions/{id}/` | GET | Public | Retrieve auction |
| `/api/auction/auctions/{id}/` | PUT | Auth | Full update auction |
| `/api/auction/auctions/{id}/` | PATCH | Auth | Partial update auction |
| `/api/auction/auctions/{id}/` | DELETE | Auth | Delete auction |

### Bids
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auction/bids/` | GET | Public | List bids |
| `/api/auction/bids/` | POST | Auth | Create bid |
| `/api/auction/bids/{id}/` | PATCH | Auth | Partial update bid |
| `/api/auction/bids/{id}/` | PUT | Auth | Full update bid |
| `/api/auction/bids/{id}/` | DELETE | Auth | Delete bid |
| `/api/auction/bids/place/` | POST | Auth | Custom bid placement (validates amount) |

---

## 🔐 Authentication
Use **JWT Authentication** for protected endpoints.

After login include:
```
Authorization: Bearer <ACCESS_TOKEN>
```

### Obtain Token
`POST /api/users/login/` (form fields: `email`, `password`)

### Example (PowerShell curl)
```powershell
curl -X POST http://127.0.0.1:8000/api/users/login/ -d "email=user@example.com" -d "password=Secret123!"
```
Response:
```json
{"access": "<token>", "refresh": "<token>"}
```

Use `access` token in subsequent calls.

### Refresh Token
`POST /api/users/token/refresh/` (form field `refresh`)

---

## 🗂 Project Structure
```
B2A2-Car-Auction-Backend/
├── auction/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── vehicles/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── car_auction/
│   ├── settings.py
│   └── urls.py
├── scripts/
│   ├── populate_vehicles.py
│   └── populate_auctions_and_bids.py
├── manage.py
└── README.md
```

---

## ⚙️ Environment Variables
Set these in your `.env` or environment:
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_USE_TLS`
- `PSWD_RESET_BASE_LINK`

---

## 📖 API Documentation & Forms
Interactive docs: `/swagger/` or `/docs/`.

All POST/PUT/PATCH endpoints accept `application/x-www-form-urlencoded` or `multipart/form-data` fields instead of JSON bodies.
File/image uploads use multipart.

Powered by helper `safe_generate_form_parameters` converting serializer fields into Swagger form inputs.

---

## 🤝 Contributing
1. Fork the repo
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

---

## 📄 License
This project is licensed under the MIT License.

---

**Made with ❤️ for car enthusiasts and auctioneers!**

---

## 🧪 Swagger Form Field Rendering

This project uses `drf-yasg` with a custom helper `utils/swagger.py` to render endpoints as HTML form fields in Swagger UI rather than a single JSON body.

### Why manual form parameters?
`drf-yasg` cannot mix certain multipart/form-data bodies (especially with file/image fields) with an OpenAPI Schema object for request bodies – this produced the error:
```
SwaggerGenerationError: form request body cannot be a Schema
```
To avoid this, endpoints are annotated using `manual_parameters` derived from serializer field definitions.

### Helper Usage
```python
from utils.swagger import safe_generate_form_parameters
@swagger_auto_schema(
    method='post',
    manual_parameters=safe_generate_form_parameters(MySerializer),
    consumes=['application/x-www-form-urlencoded','multipart/form-data']
)
```

### Adding a New Form Endpoint
1. Define/Update a DRF `Serializer`.
2. For PATCH support create Partial variant (set each field `required=False`).
3. Import `safe_generate_form_parameters`.
4. Replace `request_body=` usage with `manual_parameters=safe_generate_form_parameters(MySerializer)`.
5. Add `consumes` for form or multipart.

### Limitations
- Deep nested writes not supported (flattening only)
- `ListField` appears as a single input (bulk file handled separately)
- Validation handled server-side by DRF serializers

### Debugging Tips
If Swagger breaks:
1. Remove last decorator.
2. Check commas/indentation.
3. Verify serializer import & migrations.
4. Look for circular imports.

## 🛡 Protected API Examples

### Create Vehicle (Dealer)
```powershell
curl -X POST http://127.0.0.1:8000/api/vehicles/ ^
	-H "Authorization: Bearer <ACCESS_TOKEN>" ^
	-F vin=1HGBH41JXMN109186 -F make=Toyota -F model=Camry -F year=2023 -F color=Silver ^
	-F mileage=25000 -F transmission=Automatic -F fuel_type=Gasoline -F body_style=Sedan ^
	-F registration_number=ABC123 -F price=25000.00 -F starting_price=20000.00
```

### Bulk Upload Vehicle Images
```powershell
curl -X POST http://127.0.0.1:8000/api/vehicle-images/bulk-upload/ ^
	-H "Authorization: Bearer <ACCESS_TOKEN>" ^
	-F vehicle=<VEHICLE_ID> ^
	-F images=@C:\path\to\img1.jpg ^
	-F images=@C:\path\to\img2.jpg
```

### Place Bid
```powershell
curl -X POST http://127.0.0.1:8000/api/auction/bids/place/ ^
	-H "Authorization: Bearer <ACCESS_TOKEN>" ^
	-d auction=<AUCTION_ID> -d bid_amount=27500.00
```

### Partial Update User
```powershell
curl -X PATCH http://127.0.0.1:8000/api/users/accounts/<USER_ID>/ ^
	-H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>" ^
	-d mobile=+15551234567 -d first_name=John
```

### Password Reset Request
```powershell
curl -X POST http://127.0.0.1:8000/api/users/password-reset/ -d email=user@example.com
```

### Password Reset Confirm
```powershell
curl -X POST http://127.0.0.1:8000/api/users/password-reset/<token>/ ^
	-d new_password=NewStrongPass123! -d confirm_password=NewStrongPass123!
```

## ✅ Standards & Quality Summary

| Area | Implemented Practices |
|------|-----------------------|
| Validation | Unique email/mobile, VIN regex, year/mileage bounds, password complexity, bid amount rules |
| Security | JWT auth, dealer ownership checks, admin privilege validation on creation |
| Documentation | Form-based Swagger via `safe_generate_form_parameters`; explicit query params for listings |
| Error Handling | Graceful suppression of Operational/ProgrammingError in swagger generation |
| Modularity | Separate apps (`users`, `vehicles`, `auction`), reusable swagger utility |
| Consistency | All write endpoints form/multipart; PATCH uses partial serializers |
| Extensibility | Partial serializer pattern & helper easily extendable |

### Future Improvements
- Add rate limiting (DRF throttles)
- Add audit logging for sensitive actions
- Migrate to PostgreSQL
- Expand automated tests (PyTest)
- Add caching/ETag for list endpoints
- Introduce custom permission classes (`IsDealerOwner`, `IsAuctionOwner`)

## 🔄 Partial vs Full Update
PUT uses full serializer (required fields). PATCH uses dedicated partial serializer (all optional), reducing mandatory inputs.

---
