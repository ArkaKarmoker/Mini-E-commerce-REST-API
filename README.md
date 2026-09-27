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
- [Screenshots](#-screenshots)

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

- **🔐 Token Authentication & Profiles:** User registration with password validation, token issuance (`/api-token-auth/` & `/api/auth/login/`), token invalidation on logout, and user profile management.

- **📁 Category Management:** Full CRUD operations with Role-Based Access Control (RBAC: public read-only, admin-restricted modifications).

- **🛍️ Product Catalog & WebP Pipeline:** Comprehensive product CRUD with negative price/stock protection and an automated Pillow pipeline converting uploads to WebP.

- **🔍 Advanced Search, Filtering & Pagination:** Multi-field search (`?search=`), category & price range filtering (`?min_price=&max_price=`), ordering, and customizable page sizes (`?page_size=`).

- **🛒 Concurrency-Safe Orders:** Atomic order placement with row-level locking (`select_for_update`) to prevent overselling, automatic total calculation, user isolation, and stock restoration on cancellation.

- **⭐ Verified Purchase Reviews:** Ratings (1–5) and reviews strictly restricted to customers with `Completed` orders, duplicate review prevention, and real-time average rating calculation.

- **📖 Interactive API Docs:** Comprehensive OpenAPI 3.0 specification with live Swagger UI (`/api/docs/`), ReDoc (`/api/redoc/`), and an interactive API root index at `/`.

---

## 📊 Database Schema (ERD)

The relational schema models user accounts, authentication tokens, categories, products, orders, and verified reviews. All tables, primary keys, foreign keys, cascade behaviors, and business constraints are enforced at both the database level and the Django ORM layer.

### 📐 Mermaid Entity Relationship Diagram

```mermaid
erDiagram
    CATEGORY ||--o{ PRODUCT : "categorizes (1:N)"
    PRODUCT ||--o{ ORDER : "ordered_in (1:N)"
    PRODUCT ||--o{ REVIEW : "receives (1:N)"
    ORDER }o--|| USER : "placed_by (N:1)"
    REVIEW }o--|| USER : "written_by (N:1)"
    USER ||--o| TOKEN : "authenticates (1:1)"

    CATEGORY {
        int id PK
        string name UK
        string description
        datetime created_at
        datetime updated_at
    }

    PRODUCT {
        int id PK
        int category_id FK "CASCADE"
        string name
        string description
        decimal price "min 0.01"
        int stock "min 0"
        string image "WebP format"
        datetime created_date
        datetime updated_date
    }

    ORDER {
        int id PK
        int user_id FK "CASCADE"
        int product_id FK "CASCADE"
        int quantity "min 1"
        decimal total_price
        string status "Pending|Processing|Completed|Cancelled"
        datetime order_date
    }

    REVIEW {
        int id PK
        int product_id FK "CASCADE"
        int user_id FK "CASCADE"
        int rating "1 to 5"
        string comment
        datetime created_at
    }

    USER {
        int id PK
        string username UK
        string email
        string password
        string first_name
        string last_name
        boolean is_staff
        boolean is_superuser
        boolean is_active
        datetime date_joined
    }

    TOKEN {
        string key PK
        int user_id FK,UK "OneToOne, CASCADE"
        datetime created
    }
```

---

## 📁 Project Directory Structure

```text
Mini-E-commerce-REST-API/
├── accounts/                       # Authentication & user management
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py                    # 4 Core tests (Register, Login, Profile, Logout)
│   ├── urls.py
│   └── views.py
├── core/                           # Django project root configuration
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py                     # Root routing, API sitemap & Swagger docs
│   └── wsgi.py
├── media/
│   └── products/                   # Optimized WebP product images
├── screenshots/                    # Admin, Postman & Swagger documentation screenshots
├── orders/                         # Order processing & inventory lifecycle
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py                    # 4 Core tests (Stock deduction, Isolation, Cancel)
│   ├── urls.py
│   └── views.py                    # OrderViewSet with row-level stock locking
├── products/                       # Catalog, category & review management
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py        # Database seeding command
│   ├── migrations/
│   ├── seed_images/                # Source images for database seeding
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py                  # ProductFilter (Price range, Category, Search)
│   ├── models.py                   # Category, Product (WebP pipeline), Review
│   ├── pagination.py               # StandardResultsSetPagination (?page_size)
│   ├── permissions.py              # IsAdminOrReadOnly & IsReviewAuthor
│   ├── serializers.py
│   ├── tests.py                    # 7 Core tests (Category, Product, Filter, Review)
│   ├── urls.py
│   └── views.py
├── .gitignore
├── db.sqlite3                      # Pre-seeded database
├── manage.py
├── postman_collection.json         # Postman collection (32 endpoints & saved examples)
├── Project Requirements - Mini E-commerce REST API.md
├── README.md
└── requirements.txt
```

---

## 🚀 Installation & Local Setup

> [!NOTE]
> **Reviewer Note:** `db.sqlite3` and `media/` are included in the repo (commented out in `.gitignore`) for instant evaluation without requiring manual migrations or seeding.

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

### 5. Seed Database (Optional)
Populate the database with pre-configured users, authentication tokens, categories, products, orders, and reviews:
```bash
python manage.py seed_data
```

To perform a clean reset (Recommended — flushes existing test orders/reviews and resets auto-increment sequences back to 1):
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

Include the token in the `Authorization` HTTP header with the `Token` prefix for all protected endpoints:

| Header Key | Header Value | Example |
| :--- | :--- | :--- |
| `Authorization` | `Token <token_key>` | `Token 157e4425f7f6841c5f2597403720ffbbd74b8ab0` |

### Quick Example: Creating an Order

**Request:**
```http
POST /api/orders/
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
    "product": 1,
    "product_name": "iPhone 15 Pro Max",
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

---

## 📸 Screenshots

### 1. Interactive API Documentation & Explorer

#### 📄 Swagger UI Documentation (`/api/docs/`)
Interactive OpenAPI 3.0 specification with live request testing and schema definitions:

![Swagger UI Documentation](./screenshots/OpenAPI.jpeg)

#### 🌐 DRF Browsable API (`/`)
Root API index providing direct hyperlinked navigation to all endpoints:

![DRF Browsable API](./screenshots/DRF%20Browsable%20API.jpeg)

---

### 2. Postman Collection & Test Suite

#### 📬 Postman Collection Workspace
Complete collection with 7 functional folders, 32 endpoints, and 100% saved response examples:

![Postman Collection](./screenshots/Postman%20Collection.png)

---

### 3. Django Administration Panel

#### ⚙️ Admin Dashboard Overview (`/admin/`)
Central administrative control panel for all data models:

![Django Admin Dashboard](./screenshots/Django%20Admin%20Panel.jpeg)

#### 🛍️ Products Management
Catalog administration featuring live thumbnail previews and WebP image tracking:

![Django Admin Products](./screenshots/Django%20Admin%20Panel%20Products.jpeg)

#### 📦 Orders Lifecycle Management
Real-time order tracking with color-coded status badges (`Pending`, `Processing`, `Completed`, `Cancelled`):

![Django Admin Orders](./screenshots/Django%20Admin%20Panel%20Orders.jpeg)

#### 📁 Categories Management
Product categorization and catalog organization:

![Django Admin Categories](./screenshots/Django%20Admin%20Panel%20Categories.jpeg)

#### ⭐ Verified Customer Reviews
Customer feedback management with 1–5 star rating enforcement:

![Django Admin Reviews](./screenshots/Django%20Admin%20Panel%20Reviews.jpeg)

#### 🔑 Authentication Tokens
Cryptographic token tracking for stateless API authentication:

![Django Admin Tokens](./screenshots/Django%20Admin%20Panel%20Tokens.jpeg)

#### 👥 User Accounts Management
Customer and administrative user account management with RBAC flags:

![Django Admin Users](./screenshots/Django%20Admin%20Panel%20Users.jpeg)

