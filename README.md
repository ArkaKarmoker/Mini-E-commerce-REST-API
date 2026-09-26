# 🛒 Mini E-commerce REST API

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Django-6.1.1-092E20?style=for-the-badge&logo=django&logoColor=44B78B" alt="Django">
  <img src="https://img.shields.io/badge/Django_REST-3.18.1-ff1709?style=for-the-badge&logo=django&logoColor=white" alt="DRF">
  <img src="https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Pillow-12.3.0-FF6F00?style=for-the-badge&logo=python&logoColor=white" alt="Pillow">
  <img src="https://img.shields.io/badge/Swagger-OpenAPI_3.0-C85000?style=for-the-badge&logo=swagger&logoColor=white" alt="Swagger">
  <img src="https://img.shields.io/badge/Auth-DRF_Token-black?style=for-the-badge&logo=JSON%20web%20tokens" alt="Token Auth">
</p>

A scalable, production-ready backend REST API for an E-commerce platform built with **Django** and **Django REST Framework (DRF)**. The system provides category and product management, advanced filtering, searching, ordering, pagination, token-based authentication, concurrency-safe order processing with atomic stock validation, verified purchase reviews, automated WebP image optimization, and interactive OpenAPI 3.0 documentation.

📦 **GitHub Repository:** [Mini-E-commerce-REST-API](https://github.com/ArkaKarmoker/Mini-E-commerce-REST-API)  
👨‍💻 **Developed by:** [Arka Karmoker](https://github.com/ArkaKarmoker)  
📧 **Email:** [arkakarmoker1234@gmail.com](mailto:arkakarmoker1234@gmail.com)  
📁 **Postman Collection:** [`postman_collection.json`](./postman_collection.json)

---

## 📋 Table of Contents
- [Technology Stack](#-technology-stack)
- [Key Features](#-key-features)
- [Database Schema (ERD)](#-database-schema-erd)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Local Setup](#-installation--local-setup)
- [Demo User Credentials](#-demo-user-credentials)
- [Automated Testing](#-automated-testing)
- [API Documentation & Endpoints Reference](#-api-documentation--endpoints-reference)
- [Filtering, Searching & Ordering](#-filtering-searching--ordering)
- [Token Authentication Usage](#-token-authentication-usage)
- [Postman API Testing](#-postman-api-testing)

---

## 🛠️ Technology Stack

| Layer / Category | Technology | Details / Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ | Core runtime environment |
| **Backend Framework** | Django 6.1.1 | High-level web framework (ORM, migrations, admin) |
| **REST API Engine** | Django REST Framework (DRF) 3.18.1 | Serializers, ViewSets, APIViews, TokenAuthentication |
| **Database** | SQLite 3 | Relational database (pre-seeded with demo records) |
| **API Documentation** | drf-spectacular 0.30.0 | OpenAPI 3.0 schema generation, Swagger UI & ReDoc |
| **Filtering & Search** | django-filter 26.1 | Multi-parameter filtering, full-text search & ordering |
| **Media Optimization** | Pillow 12.3.0 | Automated conversion of uploaded images to `.webp` |
| **Authentication** | DRF TokenAuthentication | Stateless HTTP token authentication |

---

## ✨ Key Features

1. **User Authentication (Token-based)**
   - Registration (`/api/auth/register/`) with password confirmation and automatic token generation.
   - Login (`/api/auth/login/`) returning auth token and user profile details.
   - Standard DRF token retrieval (`/api-token-auth/`) via username & password.
   - Logout (`/api/auth/logout/`) invalidating and deleting active auth tokens.
   - Profile retrieval and update (`/api/auth/profile/`).

2. **Category Management**
   - Full CRUD operations: List, Retrieve, Create, Update, and Delete.
   - Role-Based Access Control (RBAC): Public read-only access, staff/admin restricted modifications.

3. **Product Management & Image Optimization**
   - Fields: Name, Description, Price, Stock, Category, Image, Created Date, Updated Date, Average Rating, Total Reviews.
   - Full CRUD operations with validation preventing negative price or negative stock.
   - Automated WebP image processing pipeline via Pillow converting uploaded JPEG/PNGs to lightweight `.webp` format.
   - Public read-only access, staff/admin restricted modifications.

4. **Product Filtering, Searching, Ordering & Pagination**
   - **Search:** Case-insensitive search across product name and description (`?search=phone`).
   - **Category Filter:** Filter by Category ID (`?category=1`) or Category Name (`?category_name=Smartphones`).
   - **Price Range Filter:** Range filtering using `min_price` and `max_price` (`?min_price=300&max_price=1000`) or exact price (`?price=299.99`).
   - **Ordering:** Ascending (`?ordering=price`) and descending (`?ordering=-price`, `?ordering=-created_date`).
   - **Custom Pagination:** Page-based pagination with configurable page size (`?page=1&page_size=5`).

5. **Order Processing & Concurrency Control**
   - Authenticated order placement specifying product ID and quantity.
   - Concurrency-safe atomic inventory deduction using database row-level locking (`select_for_update`).
   - Automatic calculation of `total_price = product.price * quantity`.
   - Strict user isolation: Customers view only their own orders; staff/admins view all orders.
   - Order cancellation (`/api/orders/{id}/cancel/`) with automatic stock restoration back to inventory.

6. **Verified Purchase Product Reviews**
   - Authenticated customers can submit a rating (1–5) and comment for products they have purchased.
   - Enforces verified purchase validation: User must have a `Completed` order for the product.
   - Prevents duplicate reviews (one review per user per product).
   - Real-time calculation of product average rating and total review count.
   - Object-level permission: Authors can update/delete their reviews; admins can moderate.

7. **Interactive API Documentation & Navigation**
   - Swagger UI (`/api/docs/`) with live interactive API testing.
   - ReDoc (`/api/redoc/`) offering clean 3-panel documentation.
   - Raw OpenAPI 3.0 schema endpoint (`/api/schema/`).
   - Clickable interactive API Root index at `/` linking directly to all endpoints.

---

## 📊 Database Schema (ERD)

The relational schema models user accounts, authentication tokens, categories, products, orders, and verified reviews:

```mermaid
erDiagram
    AUTH_USER ||--o{ ORDERS : places
    AUTH_USER ||--o{ REVIEWS : writes
    AUTH_USER ||--o| AUTHTOKEN_TOKEN : owns
    CATEGORIES ||--o{ PRODUCTS : categorizes
    PRODUCTS ||--o{ ORDERS : ordered_in
    PRODUCTS ||--o{ REVIEWS : receives

    AUTH_USER {
        int id PK
        string username UK
        string email
        string password
        string first_name
        string last_name
        boolean is_staff
        boolean is_superuser
        datetime date_joined
    }

    CATEGORIES {
        int id PK
        string name UK
        string description
        datetime created_at
        datetime updated_at
    }

    PRODUCTS {
        int id PK
        int category_id FK
        string name
        string description
        decimal price
        int stock
        string image
        datetime created_date
        datetime updated_date
    }

    ORDERS {
        int id PK
        int user_id FK
        int product_id FK
        int quantity
        decimal total_price
        string status
        datetime order_date
    }

    REVIEWS {
        int id PK
        int product_id FK
        int user_id FK
        int rating
        string comment
        datetime created_at
    }

    AUTHTOKEN_TOKEN {
        string key PK
        int user_id FK, UK
        datetime created
    }
```

---

## 📁 Project Directory Structure

```text
Mini-E-commerce-REST-API/
├── core/                           # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                 # Core settings (Installed apps, DRF, Spectacular, DB)
│   ├── urls.py                     # Root routing, API sitemap & Swagger documentation
│   └── wsgi.py
├── accounts/                       # Authentication & user management app
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py              # User registration, login, and profile serializers
│   ├── tests.py                    # Auth & profile unit tests
│   ├── urls.py                     # Auth endpoints (/register/, /login/, /logout/, /profile/)
│   └── views.py                    # RegisterView, LoginView, LogoutView, ProfileView
├── products/                       # Categories, products, and reviews app
│   ├── admin.py                    # Admin registrations with image thumbnail previews
│   ├── apps.py
│   ├── filters.py                  # ProductFilter (price range, category, search)
│   ├── models.py                   # Category, Product (WebP pipeline), and Review models
│   ├── pagination.py               # StandardResultsSetPagination
│   ├── permissions.py              # IsAdminOrReadOnly & IsReviewAuthor
│   ├── serializers.py              # Category, Product, and Review serializers
│   ├── tests.py                    # Category, Product, Filter, Search, and Review tests
│   ├── urls.py                     # Router registrations for products, categories, reviews
│   ├── views.py                    # CategoryViewSet, ProductViewSet, ReviewViewSet
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py        # Database seeding command (Users, Categories, Products, Orders, Reviews)
│   └── seed_images/                # Source product images for database seeding
├── orders/                         # Order processing & inventory app
│   ├── admin.py                    # Order admin with color-coded status badges
│   ├── apps.py
│   ├── models.py                   # Order model (User, Product, Quantity, Total Price, Status)
│   ├── serializers.py              # OrderSerializer with atomic stock validation
│   ├── tests.py                    # Order placement, concurrency, and stock restoration tests
│   ├── urls.py                     # Order router endpoints
│   └── views.py                    # OrderViewSet with select_for_update locking
├── media/                          # Uploaded and converted product images (.webp)
│   └── products/
├── .gitignore
├── db.sqlite3                      # Pre-seeded database with sample data
├── manage.py                       # Django CLI management script
├── postman_collection.json         # Postman API Collection
├── requirements.txt                # Pinned project dependencies
└── README.md
```

---

## 🚀 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/ArkaKarmoker/Mini-E-commerce-REST-API.git
cd Mini-E-commerce-REST-API
```

### 2. Create & Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Seed Database (Optional but Recommended)
Populate the database with pre-configured users, categories, products, orders, and reviews:
```bash
python manage.py seed_data
```

To perform a clean reset (flushing existing test orders/reviews and resetting auto-increment sequences back to 1):
```bash
python manage.py seed_data --clean
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
The API is available at `http://127.0.0.1:8000/`.

---

## 🔑 Demo User Credentials

The database comes pre-seeded with two ready-to-test accounts:

| Role | Username | Password | Email | Seeded Auth Token |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | `admin@example.com` | `bfd67759f593b11721125bcd9370c12764394c97` |
| **Customer** | `customer` | `customer123` | `customer@example.com` | `157e4425f7f6841c5f2597403720ffbbd74b8ab0` |

**Django Admin Panel:** Log into [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) using the Admin credentials:
- **Products Admin:** Displays live thumbnail image previews and direct clickable links.
- **Orders Admin:** Displays styled, color-coded status badges (`Pending` [Amber], `Processing` [Blue], `Completed` [Green], `Cancelled` [Red]).

---

## 🧪 Automated Testing

The project includes a concise, robust suite of **15 automated unit and integration tests** covering all core requirements:

```bash
python manage.py test
```

**Output:**
```text
Ran 15 tests in 9.922s

OK
```

Run tests by individual application module:
```bash
python manage.py test accounts
python manage.py test products
python manage.py test orders
```

---

## 📖 API Documentation & Endpoints Reference

Interactive API documentation interfaces are available out of the box:
- 🚀 **Swagger UI:** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- 📖 **ReDoc:** [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- 📜 **OpenAPI Schema (JSON):** [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
- 🌐 **Interactive API Root Index:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### 1. Authentication Endpoints (`auth`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/auth/register/` | Register a new user account & return token | No |
| `POST` | `/api/auth/login/` | Authenticate user & retrieve auth token | No |
| `POST` | `/api-token-auth/` | Obtain DRF auth token via username & password | No |
| `POST` | `/api/auth/logout/` | Invalidate & delete active auth token | Token |
| `GET` | `/api/auth/profile/` | Retrieve logged-in user profile details | Token |
| `PUT` | `/api/auth/profile/` | Full update of user profile details | Token |
| `PATCH` | `/api/auth/profile/` | Partial update of user profile details | Token |

### 2. Category Endpoints (`categories`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/categories/` | List all categories | No |
| `GET` | `/api/categories/{id}/` | Retrieve single category details | No |
| `POST` | `/api/categories/` | Create a new category | Admin / Staff |
| `PUT` | `/api/categories/{id}/` | Full update of category | Admin / Staff |
| `PATCH` | `/api/categories/{id}/` | Partial update of category | Admin / Staff |
| `DELETE` | `/api/categories/{id}/` | Delete a category | Admin / Staff |

### 3. Product Endpoints (`products`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/products/` | List products with filtering, search & pagination | No |
| `GET` | `/api/products/{id}/` | Retrieve single product details & average rating | No |
| `POST` | `/api/products/` | Create a new product (supports image upload) | Admin / Staff |
| `PUT` | `/api/products/{id}/` | Full update of product details | Admin / Staff |
| `PATCH` | `/api/products/{id}/` | Partial update of product details | Admin / Staff |
| `DELETE` | `/api/products/{id}/` | Delete a product | Admin / Staff |

### 4. Review Endpoints (`reviews`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/products/{id}/reviews/` | List all verified reviews for a specific product | No |
| `POST` | `/api/products/{id}/reviews/` | Add review (Rating 1–5, requires `Completed` order) | Token |
| `GET` | `/api/reviews/` | List all product reviews | No |
| `GET` | `/api/reviews/{id}/` | Retrieve a single review | No |
| `PUT` | `/api/reviews/{id}/` | Full update of review | Author |
| `PATCH` | `/api/reviews/{id}/` | Partial update of review | Author |
| `DELETE` | `/api/reviews/{id}/` | Delete a review | Author / Admin |

### 5. Order Endpoints (`orders`)

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/orders/` | List orders (Customer views own; Admin views all) | Token |
| `POST` | `/api/orders/` | Place a new order with atomic stock validation | Token |
| `GET` | `/api/orders/{id}/` | Retrieve single order details | Token |
| `POST` | `/api/orders/{id}/cancel/` | Cancel pending order & restore stock | Token |

---

## 🔍 Filtering, Searching & Ordering

The `/api/products/` endpoint supports multi-parameter filtering, full-text searching, ordering, and pagination:

| Parameter | Type | Example | Description |
| :--- | :--- | :--- | :--- |
| `search` | String | `?search=macbook` | Full-text search across product `name` and `description` |
| `category` | Integer | `?category=1` | Filter products by Category ID |
| `category_name` | String | `?category_name=Laptops` | Case-insensitive filter by category name |
| `min_price` | Decimal | `?min_price=500` | Filter products with price $\ge$ `min_price` |
| `max_price` | Decimal | `?max_price=1500` | Filter products with price $\le$ `max_price` |
| `price` | Decimal | `?price=249.99` | Filter products with exact price match |
| `ordering` | String | `?ordering=price` | Ascending sort by price or date (`price`, `created_date`) |
| `ordering` | String | `?ordering=-price` | Descending sort by price or date (`-price`, `-created_date`) |
| `page` | Integer | `?page=2` | Target page number |
| `page_size` | Integer | `?page_size=5` | Number of items per page |

### Example Queries
- **Search by keyword:**
  ```http
  GET /api/products/?search=pro
  ```
- **Filter by price range and sort descending:**
  ```http
  GET /api/products/?min_price=200&max_price=1000&ordering=-price
  ```
- **Filter by category name with custom pagination:**
  ```http
  GET /api/products/?category_name=Smartphones&page=1&page_size=4
  ```
- **Combined multi-parameter query:**
  ```http
  GET /api/products/?category=1&min_price=500&ordering=-price&search=apple
  ```

---

## 🔒 Token Authentication Usage

Authenticate requests to protected endpoints by passing the token in the `Authorization` HTTP header:

```http
Authorization: Token <your_token_here>
```

### Example: Creating an Order

**Request:**
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

**Response (`201 Created`):**
```json
{
    "id": 6,
    "user": "customer",
    "user_id": 2,
    "product": 1,
    "product_name": "iPhone 15 Pro Max",
    "product_price": "1199.99",
    "quantity": 2,
    "total_price": "2399.98",
    "status": "Pending",
    "order_date": "2026-09-27T01:50:00.000000Z"
}
```

---

## 📬 Postman API Testing

A ready-to-use Postman collection is included in the root directory: [`postman_collection.json`](./postman_collection.json).

### How to Use:
1. Open **Postman**.
2. Click **Import** and select `postman_collection.json`.
3. The collection is pre-configured with environment variables:
   - `{{base_url}}`: `http://127.0.0.1:8000`
   - `{{admin_token}}`: `bfd67759f593b11721125bcd9370c12764394c97`
   - `{{user_token}}`: `157e4425f7f6841c5f2597403720ffbbd74b8ab0`
4. Execute the requests in sequence to test authentication, categories, products, filtering, orders, and reviews.
