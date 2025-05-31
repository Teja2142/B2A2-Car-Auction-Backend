# 🚗 B2A2 Car Auction Backend

Welcome to the backend for **B2A2 Car Auction** – a Django REST API for managing car auctions, bidding, and user authentication.

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

- User registration, login, and password reset
- Token-based authentication
- CRUD for vehicles, auctions, and bids
- Image upload for vehicles
- Secure endpoints with permission control
- Admin dashboard

---

## 🛠 Tech Stack

- **Backend:** Django, Django REST Framework
- **Database:** SQLite (default), easy to switch to PostgreSQL/MySQL
- **Authentication:** DRF Token Authentication
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

### User Endpoints

| Endpoint                        | Method | Auth      | Description                |
|----------------------------------|--------|-----------|----------------------------|
| `/api/users/register/`           | POST   | No        | Register a new user        |
| `/api/users/login/`              | POST   | No        | Login and get token        |
| `/api/users/password-reset/`     | POST   | No        | Request password reset     |
| `/api/users/password-reset/<token>/` | POST | No    | Reset password             |

### Auction Endpoints

| Endpoint                        | Method | Auth      | Description                |
|----------------------------------|--------|-----------|----------------------------|
| `/api/auction/vehicles/`         | GET    | No        | List all vehicles          |
| `/api/auction/vehicles/`         | POST   | Yes       | Create a vehicle           |
| `/api/auction/auctions/`         | GET    | No        | List all auctions          |
| `/api/auction/auctions/`         | POST   | Yes       | Create an auction          |
| `/api/auction/bids/`             | GET    | No        | List all bids              |
| `/api/auction/bids/`             | POST   | Yes       | Place a bid                |
| `/api/auction/bids/place/`       | POST   | Yes       | Place a bid (custom)       |

---

## 🔐 Authentication

- Use **Token Authentication**.
- After login, include your token in the `Authorization` header:

```
Authorization: Token <your_token>
```

---

## 🗂 Project Structure

```
B2A2-Car-Auction-Backend/
├── auction/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── users/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── car_auction/
│   ├── settings.py
│   └── urls.py
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