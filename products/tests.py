from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from orders.models import Order
from .models import Category, Product, Review


class CategoryAPITests(APITestCase):
    """
    Tests for Category API:
    - Create a category
    - View all categories
    - View a single category
    - Update a category
    - Delete a category
    - Staff/Admin permissions for modifications
    """

    def setUp(self):
        self.categories_url = '/api/categories/'

        # Users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!'
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='RegularPassword123!'
        )
        self.regular_token = Token.objects.create(user=self.regular_user)

        # Sample category
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic gadgets and devices'
        )
        self.category_detail_url = f'/api/categories/{self.category.id}/'

    def test_view_all_categories_unauthenticated(self):
        """Public users can view all categories."""
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check paginated response
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]['name'], 'Electronics')

    def test_view_single_category_unauthenticated(self):
        """Public users can view a single category."""
        response = self.client.get(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')

    def test_create_category_admin_success(self):
        """Admin/staff user can create a new category."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        payload = {'name': 'Books', 'description': 'Novels and textbooks'}
        response = self.client.post(self.categories_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Books')
        self.assertTrue(Category.objects.filter(name='Books').exists())

    def test_create_category_regular_user_forbidden(self):
        """Non-admin user cannot create a category (403 Forbidden)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.regular_token.key}')
        payload = {'name': 'Clothing', 'description': 'Apparel and shoes'}
        response = self.client.post(self.categories_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category_admin_success(self):
        """Admin/staff user can update a category."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        payload = {'name': 'Consumer Electronics', 'description': 'Updated description'}
        response = self.client.put(self.category_detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Consumer Electronics')

    def test_delete_category_admin_success(self):
        """Admin/staff user can delete a category."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.delete(self.category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=self.category.id).exists())


class ProductAPITests(APITestCase):
    """
    Tests for Product API:
    - Add a product
    - View products
    - View product details
    - Update a product
    - Delete a product
    - Search by product name
    - Filter by category
    - Filter by price
    - Order by price
    - Pagination
    """

    def setUp(self):
        self.products_url = '/api/products/'

        # Users
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!'
        )
        self.admin_token = Token.objects.create(user=self.admin)

        self.user = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='BuyerPassword123!'
        )
        self.user_token = Token.objects.create(user=self.user)

        # Categories
        self.cat_phones = Category.objects.create(name='Smartphones', description='Mobile phones')
        self.cat_laptops = Category.objects.create(name='Laptops', description='Notebooks and ultrabooks')

        # Products
        self.p1 = Product.objects.create(
            category=self.cat_phones,
            name='iPhone 15 Pro',
            description='Flagship Apple smartphone',
            price=Decimal('999.99'),
            stock=15
        )
        self.p2 = Product.objects.create(
            category=self.cat_phones,
            name='Samsung Galaxy S24',
            description='Android flagship phone',
            price=Decimal('799.99'),
            stock=20
        )
        self.p3 = Product.objects.create(
            category=self.cat_laptops,
            name='MacBook Air M3',
            description='Lightweight Apple laptop',
            price=Decimal('1099.99'),
            stock=8
        )
        self.p4 = Product.objects.create(
            category=self.cat_laptops,
            name='Budget Laptop',
            description='Affordable laptop for students',
            price=Decimal('299.99'),
            stock=5
        )

    def test_view_products_list(self):
        """Test viewing all products with pagination."""
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['count'], 4)

    def test_view_product_details(self):
        """Test viewing a single product's detail."""
        detail_url = f'{self.products_url}{self.p1.id}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'iPhone 15 Pro')
        self.assertEqual(response.data['category']['name'], 'Smartphones')
        self.assertIn('reviews', response.data)

    def test_add_product_admin_success(self):
        """Admin can add a new product."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        payload = {
            'name': 'Google Pixel 8',
            'description': 'Pure Android smartphone',
            'price': '699.99',
            'stock': 10,
            'category': self.cat_phones.id
        }
        response = self.client.post(self.products_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Google Pixel 8')
        self.assertEqual(response.data['stock'], 10)

    def test_add_product_negative_price_rejected(self):
        """Product with negative or zero price should be rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        payload = {
            'name': 'Invalid Product',
            'price': '-10.00',
            'stock': 5,
            'category': self.cat_phones.id
        }
        response = self.client.post(self.products_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)

    def test_add_product_regular_user_forbidden(self):
        """Regular user cannot add a product."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        payload = {
            'name': 'Google Pixel 8',
            'price': '699.99',
            'stock': 10,
            'category': self.cat_phones.id
        }
        response = self.client.post(self.products_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_product_admin_success(self):
        """Admin can update product details."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        detail_url = f'{self.products_url}{self.p1.id}/'
        payload = {
            'name': 'iPhone 15 Pro Max',
            'description': 'Updated flagship phone',
            'price': '1199.99',
            'stock': 25,
            'category': self.cat_phones.id
        }
        response = self.client.put(detail_url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.name, 'iPhone 15 Pro Max')
        self.assertEqual(self.p1.stock, 25)

    def test_delete_product_admin_success(self):
        """Admin can delete a product."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        detail_url = f'{self.products_url}{self.p4.id}/'
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.p4.id).exists())

    def test_search_by_product_name(self):
        """Test searching products by name (?search=phone)."""
        response = self.client.get(f'{self.products_url}?search=phone')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in response.data['results']]
        self.assertIn('iPhone 15 Pro', names)
        self.assertIn('Samsung Galaxy S24', names)
        self.assertNotIn('MacBook Air M3', names)

    def test_filter_by_category_id(self):
        """Test filtering products by category ID (?category=X)."""
        response = self.client.get(f'{self.products_url}?category={self.cat_laptops.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        for prod in results:
            self.assertEqual(prod['category'], self.cat_laptops.id)

    def test_filter_by_category_name(self):
        """Test filtering products by category name (?category=Laptops)."""
        response = self.client.get(f'{self.products_url}?category=Laptops')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        for prod in results:
            self.assertEqual(prod['category'], self.cat_laptops.id)

    def test_filter_by_price_range(self):
        """Test filtering by min_price and max_price."""
        response = self.client.get(f'{self.products_url}?min_price=700&max_price=1000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in response.data['results']]
        self.assertIn('iPhone 15 Pro', names)
        self.assertIn('Samsung Galaxy S24', names)
        self.assertNotIn('Budget Laptop', names)
        self.assertNotIn('MacBook Air M3', names)

    def test_ordering_by_price_ascending(self):
        """Test ordering by price ascending (?ordering=price)."""
        response = self.client.get(f'{self.products_url}?ordering=price')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(p['price']) for p in response.data['results']]
        self.assertEqual(prices, sorted(prices))

    def test_ordering_by_price_descending(self):
        """Test ordering by price descending (?ordering=-price)."""
        response = self.client.get(f'{self.products_url}?ordering=-price')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(p['price']) for p in response.data['results']]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_pagination(self):
        """Test pagination parameter (?page=1&page_size=2)."""
        response = self.client.get(f'{self.products_url}?page=1&page_size=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['count'], 4)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertIsNotNone(response.data['next'])

    def test_product_review_and_rating(self):
        """Test submitting product review and rating calculation when order is completed."""
        # Create a Completed order for this user and product
        Order.objects.create(
            user=self.user,
            product=self.p1,
            quantity=1,
            total_price=self.p1.price,
            status='Completed'
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        review_url = f'{self.products_url}{self.p1.id}/reviews/'

        payload = {'rating': 5, 'comment': 'Amazing phone! Highly recommended.'}
        response = self.client.post(review_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 5)

        # Check product average rating
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.average_rating, 5.0)
        self.assertEqual(self.p1.total_reviews, 1)

        # Submitting second review by same user on same product should be rejected
        second_response = self.client.post(review_url, payload)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_product_review_requires_completed_order(self):
        """Review submission must be blocked if user has not purchased or order is not Completed."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.user_token.key}')
        review_url = f'{self.products_url}{self.p2.id}/reviews/'
        payload = {'rating': 4, 'comment': 'Nice product'}

        # 1. No order at all -> 400 Bad Request
        res_no_order = self.client.post(review_url, payload)
        self.assertEqual(res_no_order.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", res_no_order.data)

        # 2. Order exists but status is 'Pending' -> 400 Bad Request
        order = Order.objects.create(
            user=self.user,
            product=self.p2,
            quantity=1,
            total_price=self.p2.price,
            status='Pending'
        )
        res_pending = self.client.post(review_url, payload)
        self.assertEqual(res_pending.status_code, status.HTTP_400_BAD_REQUEST)

        # 3. Order status updated to 'Processing' -> still 400 Bad Request
        order.status = 'Processing'
        order.save()
        res_processing = self.client.post(review_url, payload)
        self.assertEqual(res_processing.status_code, status.HTTP_400_BAD_REQUEST)

        # 4. Order status updated to 'Completed' -> 201 Created!
        order.status = 'Completed'
        order.save()
        res_completed = self.client.post(review_url, payload)
        self.assertEqual(res_completed.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_completed.data['rating'], 4)

