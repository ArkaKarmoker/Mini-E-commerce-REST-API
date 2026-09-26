# 🛒 Mini E-commerce REST API

A robust, fully-featured **Mini E-commerce REST API** built with **Django REST Framework (DRF)**.

This project implements modern e-commerce RESTful architectures, including category and product management, advanced filtering, searching, ordering, pagination, token-based authentication, user order processing with atomic stock validation, product reviews, and auto-generated OpenAPI/Swagger documentation.

---

## 🌟 Key Features

1. **User Authentication (Token-based)**
   - Registration (`/api/auth/register/`) with password confirmation and automatic token generation.
   - Login (`/api/auth/login/`) returning auth token and user profile.
   - Logout (`/api/auth/logout/`) invalidating and deleting auth tokens.
   - Profile management (`/api/auth/profile/`).

2. **Category Management**
   - Full CRUD: Create, View all, View single, Update, Delete.
   - Public read access, staff/admin-restricted modifications.

3. **Product Management**
   - Fields: Name, Description, Price, Stock, Category, Image, Created Date, Updated Date, Average Rating, Total Reviews.
   - Full CRUD: Add, View all, View single, Update, Delete.
   - Validation against negative price or negative stock.
   - Public read access, staff/admin-restricted modifications.

4. **Product Filtering, Searching, Ordering & Pagination**
   - **Search:** Full-text search by product name and description (e.g., `/products/?search=phone`).
   - **Category Filter:** Filter by Category ID (e.g., `/products/?category=1`) or Category Name (`/products/?category_name=Smartphones`).
   - **Price Filter:** Range filtering using `min_price` and `max_price` (e.g., `/products/?min_price=100&max_price=800`) or exact price (`/products/?price=299.99`).
   - **Ordering:** Order ascending (`/products/?ordering=price`) or descending (`/products/?ordering=-price`).
   - **Pagination:** Customizable page size via query parameter (e.g., `/products/?page=1&page_size=10`).

5. **Order Management & Stock Validation**
   - Authenticated users can place orders specifying a product and quantity.
   - **Stock Validation:** Automatic check against current inventory. Prevents over-ordering and race conditions using atomic database transactions (`select_for_update`).
   - **Automatic Total Calculation:** Automatically calculates `total_price = product.price * quantity`.
   - **User Isolation:** Customers can only view their own orders; staff/admin can view all orders.
   - **Order Cancellation:** Customers can cancel pending orders, automatically restoring inventory back to the product stock.

6. **Optional Bonus Features Implemented**
   - **Product Reviews & Ratings:** Authenticated users can review products (rating 1-5 and comment) once their order status is 'Completed', preventing duplicate reviews and computing dynamic average ratings.
   - **Product Image Support:** Supports image uploads for products.
   - **Seed Data Command:** Ready-to-use sample dataset with admin and demo customer credentials.
   - **Interactive API Documentation:** Swagger UI and ReDoc interfaces with OpenAPI 3.0 schema.
   - **Postman Collection:** Ready-to-import `postman_collection.json`.

---

## 🛠️ Technology Stack

- **Python:** 3.12+
- **Django:** 6.1.1 (Settings located in `core/` folder)
- **Django REST Framework (DRF):** 3.18.1
- **django-filter:** 26.1
- **Pillow:** 12.3.0
- **drf-spectacular:** 0.30.0 (OpenAPI 3.0 / Swagger documentation)
- **Database:** SQLite (development default)

---

## 📁 Project Structure

```text
Mini-E-commerce-REST-API/
├── core/                           # Django project configuration folder
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # Core project settings
│   ├── urls.py                     # Root routing & documentation
│   └── wsgi.py
├── accounts/                       # Authentication & user profile app
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── products/                       # Categories, products, and reviews app
│   ├── filters.py                  # Custom django-filter definitions
│   ├── models.py                   # Category, Product, and Review models
│   ├── pagination.py               # Custom standard pagination
│   ├── permissions.py              # IsAdminOrReadOnly & IsReviewAuthor
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   ├── tests.py
│   └── management/commands/
│       └── seed_data.py            # Initial database population command
├── orders/                         # Order placement & stock validation app
│   ├── models.py                   # Order model
│   ├── serializers.py              # OrderSerializer with stock deduction
│   ├── urls.py
│   ├── views.py
│   └── tests.py
├── media/                          # Uploaded product images
├── postman_collection.json         # Postman collection for API testing
├── requirements.txt                # Top-level dependencies with versions
├── manage.py
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/ArkaKarmoker/Mini-E-commerce-REST-API.git
cd Mini-E-commerce-REST-API
```

### 2. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the top-level dependencies listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Seed Demo Data (Optional but Recommended)

Populate the database with pre-configured categories, products, demo orders, and users:
```bash
python manage.py seed_data
```

To reset/clean existing test orders, reviews, and products back to the original stock for a completely fresh start:
```bash
python manage.py seed_data --clean
```

This creates:
- **Admin User:** `admin` / `admin123` (Email: `admin@example.com`)
- **Customer User:** `customer` / `customer123` (Email: `customer@example.com`)

### 6. Start Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

---

## 🧪 Running Tests

A comprehensive suite of **55 automated unit, integration, and security tests** covers all authentication flows, category operations, product filtering/searching/ordering/pagination, stock validation, and order management:

```bash
python manage.py test
```

To test individual apps:
```bash
python manage.py test accounts
python manage.py test products
python manage.py test orders
```

---

## 📖 API Documentation & Endpoints

Interactive documentation is available when the server is running:
- **Swagger UI:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc:** [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI Schema (JSON):** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register new user & receive token | No |
| `POST` | `/api/auth/login/` | Login with username/password & get token | No |
| `POST` | `/api-token-auth/` | Standard DRF endpoint to obtain token | No |
| `POST` | `/api/auth/logout/` | Invalidate & delete user token | Token |
| `GET` | `/api/auth/profile/` | View current user's profile | Token |
| `PUT/PATCH` | `/api/auth/profile/` | Update current user's profile | Token |

### Category Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/categories/` | List all categories | No |
| `GET` | `/api/categories/<id>/` | View single category details | No |
| `POST` | `/api/categories/` | Create a new category | Admin/Staff |
| `PUT/PATCH` | `/api/categories/<id>/` | Update a category | Admin/Staff |
| `DELETE` | `/api/categories/<id>/` | Delete a category | Admin/Staff |

### Product Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/products/` | List products (with filtering, pagination) | No |
| `GET` | `/api/products/<id>/` | View product details (with reviews & rating) | No |
| `POST` | `/api/products/` | Add a new product | Admin/Staff |
| `PUT/PATCH` | `/api/products/<id>/` | Update a product | Admin/Staff |
| `DELETE` | `/api/products/<id>/` | Delete a product | Admin/Staff |
| `GET` | `/api/products/<id>/reviews/` | View all reviews for a product | No |
| `POST` | `/api/products/<id>/reviews/` | Add review/rating for a product | Token |

### Order Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/orders/` | View authenticated user's orders | Token |
| `POST` | `/api/orders/` | Create a new order (with stock validation) | Token |
| `GET` | `/api/orders/<id>/` | View a single order belonging to user | Token |
| `POST` | `/api/orders/<id>/cancel/` | Cancel pending order & refund stock | Token |

---

## 🔍 Filtering, Searching & Ordering Examples

Both `/products/` and `/api/products/` are supported:

- **Search by Product Name / Description:**
  ```http
  GET /api/products/?search=phone
  ```
- **Filter by Category ID:**
  ```http
  GET /api/products/?category=1
  ```
- **Filter by Category Name:**
  ```http
  GET /api/products/?category_name=Smartphones
  ```
- **Filter by Price Range:**
  ```http
  GET /api/products/?min_price=300&max_price=1000
  ```
- **Order by Price (Ascending):**
  ```http
  GET /api/products/?ordering=price
  ```
- **Order by Price (Descending):**
  ```http
  GET /api/products/?ordering=-price
  ```
- **Custom Pagination:**
  ```http
  GET /api/products/?page=1&page_size=5
  ```
- **Combine Filters:**
  ```http
  GET /api/products/?category=1&min_price=500&ordering=-price&search=pro
  ```

---

## 🔒 Token Authentication Usage

When making requests to protected endpoints, pass the authorization header:

```http
Authorization: Token <your_token_here>
```

Example request to create an order:

```http
POST /api/orders/ HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Token 157e4425f7f6841c5f2597403720ffbbd74b8ab0
Content-Type: application/json

{
    "product": 1,
    "quantity": 2
}
```

Response:

```json
{
    "id": 1,
    "user": "customer",
    "user_id": 2,
    "product": 1,
    "product_name": "iPhone 15 Pro Max",
    "product_price": "1199.99",
    "quantity": 2,
    "total_price": "2399.98",
    "status": "Pending",
    "order_date": "2026-09-24T22:25:15.123456Z"
}
```

---

## 📬 Postman Testing

A pre-built Postman collection is included in the root directory: [`postman_collection.json`](postman_collection.json).

### How to use:
1. Open **Postman**.
2. Click **Import** and select `postman_collection.json`.
3. The collection is pre-configured with:
   - `{{base_url}}`: `http://127.0.0.1:8000`
   - `{{admin_token}}`: pre-seeded admin token
   - `{{user_token}}`: pre-seeded customer token
4. Run requests in sequence to test authentication, categories, products, filters, reviews, and orders!
