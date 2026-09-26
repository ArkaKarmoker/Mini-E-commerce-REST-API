from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from orders.models import Order
from .models import Category, Product


class ProductCatalogAndCategoryTests(APITestCase):
    """
    Core test suite for Categories, Products, Filters, Search, Ordering, Pagination, and Reviews.
    """

    def setUp(self):
        # Admin & Customer users
        self.admin = User.objects.create_superuser(
            username='admin_boss',
            email='admin@example.com',
            password='AdminPassword123!'
        )
        self.admin_token = Token.objects.create(user=self.admin)

        self.customer = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='Password123!'
        )
        self.customer_token = Token.objects.create(user=self.customer)

        # Pre-seed categories & products
        self.cat_phones = Category.objects.create(name='Smartphones', description='Phones')
        self.cat_laptops = Category.objects.create(name='Laptops', description='Laptops')

        self.p1 = Product.objects.create(
            category=self.cat_phones,
            name='iPhone 15 Pro',
            description='Apple flagship smartphone',
            price=Decimal('999.00'),
            stock=10
        )
        self.p2 = Product.objects.create(
            category=self.cat_phones,
            name='Samsung Galaxy S24',
            description='Samsung Android flagship phone',
            price=Decimal('799.00'),
            stock=5
        )
        self.p3 = Product.objects.create(
            category=self.cat_laptops,
            name='MacBook Pro 16',
            description='Apple M3 laptop computer',
            price=Decimal('2499.00'),
            stock=8
        )

    def test_category_crud_and_permissions(self):
        """1. Full Category CRUD (Admin only for modifications; public for read; customer 403)."""
        # Public List & Detail
        list_resp = self.client.get('/api/categories/')
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        # Customer forbidden from creating category (403)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        forbidden_resp = self.client.post('/api/categories/', {'name': 'Tablets', 'description': 'Tablets'})
        self.assertEqual(forbidden_resp.status_code, status.HTTP_403_FORBIDDEN)

        # Admin creates category (201)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        create_resp = self.client.post('/api/categories/', {'name': 'Tablets', 'description': 'Tablets'})
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        cat_id = create_resp.data['id']

        # Admin updates and deletes category (200, 204)
        update_resp = self.client.patch(f'/api/categories/{cat_id}/', {'description': 'Updated'})
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        del_resp = self.client.delete(f'/api/categories/{cat_id}/')
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_product_crud_and_permissions(self):
        """2. Full Product CRUD (Admin creates/updates/deletes; public reads; customer 403)."""
        # Public View Products & Details
        list_resp = self.client.get('/api/products/')
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        detail_resp = self.client.get(f'/api/products/{self.p1.id}/')
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_resp.data['name'], 'iPhone 15 Pro')

        # Customer forbidden from creating product (403)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        forbidden_resp = self.client.post('/api/products/', {
            'name': 'Hacker Device', 'price': '100.00', 'stock': 1, 'category': self.cat_phones.id
        })
        self.assertEqual(forbidden_resp.status_code, status.HTTP_403_FORBIDDEN)

        # Admin adds product (201)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        create_resp = self.client.post('/api/products/', {
            'name': 'Google Pixel 8', 'description': 'Pixel phone',
            'price': '699.00', 'stock': 15, 'category': self.cat_phones.id
        })
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        prod_id = create_resp.data['id']

        # Admin updates and deletes product (200, 204)
        update_resp = self.client.patch(f'/api/products/{prod_id}/', {'price': '649.00'})
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)

        del_resp = self.client.delete(f'/api/products/{prod_id}/')
        self.assertEqual(del_resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_product_negative_price_rejected(self):
        """3. Validation rejects products with negative price."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        payload = {
            'name': 'Free Gadget', 'description': 'Invalid price',
            'price': '-50.00', 'stock': 5, 'category': self.cat_phones.id
        }
        response = self.client.post('/api/products/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_product_search(self):
        """4. Search products by keyword across name and description."""
        response = self.client.get('/api/products/?search=galaxy')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Samsung Galaxy S24')

    def test_product_filtering(self):
        """5. Filter products by category and price range (min_price & max_price)."""
        # Filter by Category
        cat_resp = self.client.get(f'/api/products/?category={self.cat_laptops.id}')
        self.assertEqual(cat_resp.status_code, status.HTTP_200_OK)
        cat_results = cat_resp.data.get('results', cat_resp.data)
        self.assertEqual(len(cat_results), 1)
        self.assertEqual(cat_results[0]['name'], 'MacBook Pro 16')

        # Filter by Price Range
        price_resp = self.client.get('/api/products/?min_price=700&max_price=1000')
        self.assertEqual(price_resp.status_code, status.HTTP_200_OK)
        price_results = price_resp.data.get('results', price_resp.data)
        self.assertEqual(len(price_results), 2)

    def test_product_ordering_and_pagination(self):
        """6. Order by price descending and custom page size pagination."""
        response = self.client.get('/api/products/?ordering=-price&page=1&page_size=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertEqual(len(response.data['results']), 2)
        # Highest price first
        self.assertEqual(response.data['results'][0]['name'], 'MacBook Pro 16')

    def test_product_verified_review_and_rating(self):
        """7. Reviews require completed order and dynamically compute product average rating."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')

        # Attempt review without purchase -> 400 Bad Request
        unverified_resp = self.client.post(f'/api/products/{self.p1.id}/reviews/', {
            'rating': 5, 'comment': 'Fake review'
        })
        self.assertEqual(unverified_resp.status_code, status.HTTP_400_BAD_REQUEST)

        # Place a Completed order for customer
        Order.objects.create(
            user=self.customer, product=self.p1, quantity=1,
            total_price=self.p1.price, status='Completed'
        )

        # Submit verified review -> 201 Created
        verified_resp = self.client.post(f'/api/products/{self.p1.id}/reviews/', {
            'rating': 5, 'comment': 'Excellent smartphone!'
        })
        self.assertEqual(verified_resp.status_code, status.HTTP_201_CREATED)

        # Average rating updated on product
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.average_rating, 5.0)
        self.assertEqual(self.p1.total_reviews, 1)
