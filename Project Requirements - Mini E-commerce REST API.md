# 🛒 Mini E-commerce REST API

## Assignment Objective

Build a simple **Mini E-commerce REST API** using **Django REST Framework (DRF)**.

The main goal of this assignment is to practice **REST APIs, serializers, relationships, authentication, filtering, searching, ordering, pagination, and API testing**.

---

## Required Features

### 1. Category API

Create APIs to:
* Create a category
* View all categories
* View a single category
* Update a category
* Delete a category

### 2. Product API

Each product should have:
* Name
* Description
* Price
* Stock
* Category
* Created date

Create APIs to:
* Add a product
* View products
* View product details
* Update a product
* Delete a product

### 3. Product Filtering & Searching

The product API should support:
* Search by product name
* Filter by category
* Filter by price
* Order by price
* Pagination

**Example:**
* `/products/?search=phone`
* `/products/?category=1`
* `/products/?ordering=price`

### 4. User Authentication

Implement **Token Authentication**.

Authenticated users should be able to:
* Login and receive a token
* Access protected APIs using the token

### 5. Order API

A logged-in user can create an order.

An order should contain:
* User
* Product
* Quantity
* Total price
* Order date

Users should be able to:
* Create an order
* View their orders
* View a single order

---

## API Requirements

Use **Django REST Framework** and implement the APIs using:
* Serializers
* APIView or ModelViewSet
* URL routing
* Model relationships
* Token Authentication
* Filtering
* Searching
* Ordering
* Pagination
* Postman for API testing

---

## Optional

Students can add:
* Product reviews
* Product rating
* Stock validation
* Product image

> **Note:** These are **optional** and not required for the main assignment.

---

## Submission Guideline

Submit the **GitHub URL of your project**.

Your GitHub repository should contain:
* Complete source code
* `requirements.txt`
* `README.md`
* Proper project structure