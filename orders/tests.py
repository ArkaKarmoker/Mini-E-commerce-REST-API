from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from products.models import Category, Product
from .models import Order


class OrderAPITests(APITestCase):
    """
    Tests for Order API:
    - Create an order (authenticated)
    - View their orders
    - View a single order
    - Stock validation
    - Order cancellation and stock restoration
    - Isolation between users
    """

    def setUp(self):
        self.orders_url = '/api/orders/'

        # Users
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='AlicePassword123!'
        )
        self.token1 = Token.objects.create(user=self.user1)

        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='BobPassword123!'
        )
        self.token2 = Token.objects.create(user=self.user2)

        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPassword123!'
        )
        self.admin_token = Token.objects.create(user=self.admin)

        # Category and Product
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            category=self.category,
            name='Wireless Headphones',
            description='Noise-cancelling over-ear headphones',
            price=Decimal('150.00'),
            stock=10
        )

    def test_create_order_unauthenticated_fails(self):
        """Unauthenticated user cannot create an order."""
        payload = {'product': self.product.id, 'quantity': 1}
        response = self.client.post(self.orders_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order_success(self):
        """Authenticated user can place an order, total_price is calculated, and stock is deducted."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        payload = {'product': self.product.id, 'quantity': 3}
        response = self.client.post(self.orders_url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], 'alice')
        self.assertEqual(response.data['product'], self.product.id)
        self.assertEqual(response.data['quantity'], 3)
        self.assertEqual(Decimal(response.data['total_price']), Decimal('450.00'))

        # Check stock deduction
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

    def test_create_order_insufficient_stock(self):
        """Ordering more than available stock returns 400 and preserves stock."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        payload = {'product': self.product.id, 'quantity': 15}  # Stock is only 10
        response = self.client.post(self.orders_url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)

        # Stock remains untouched
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_create_order_invalid_quantity(self):
        """Ordering 0 or negative quantity is rejected."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        payload = {'product': self.product.id, 'quantity': 0}
        response = self.client.post(self.orders_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_view_own_orders(self):
        """User can view only their own orders."""
        # Create order for Alice
        order_alice = Order.objects.create(
            user=self.user1,
            product=self.product,
            quantity=1,
            total_price=Decimal('150.00')
        )
        # Create order for Bob
        order_bob = Order.objects.create(
            user=self.user2,
            product=self.product,
            quantity=2,
            total_price=Decimal('300.00')
        )

        # Alice views orders
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], order_alice.id)
        self.assertEqual(results[0]['user'], 'alice')

    def test_view_single_order_own(self):
        """User can view details of their own order."""
        order = Order.objects.create(
            user=self.user1,
            product=self.product,
            quantity=2,
            total_price=Decimal('300.00')
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        detail_url = f'{self.orders_url}{order.id}/'
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], order.id)
        self.assertEqual(response.data['quantity'], 2)
        self.assertEqual(Decimal(response.data['total_price']), Decimal('300.00'))

    def test_user_cannot_view_other_users_order(self):
        """User cannot view another user's order (should return 404)."""
        order_bob = Order.objects.create(
            user=self.user2,
            product=self.product,
            quantity=1,
            total_price=Decimal('150.00')
        )

        # Alice tries to view Bob's order
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        detail_url = f'{self.orders_url}{order_bob.id}/'
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_view_all_orders(self):
        """Admin user can view all orders from all users."""
        Order.objects.create(
            user=self.user1,
            product=self.product,
            quantity=1,
            total_price=Decimal('150.00')
        )
        Order.objects.create(
            user=self.user2,
            product=self.product,
            quantity=2,
            total_price=Decimal('300.00')
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        response = self.client.get(self.orders_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_cancel_order_restores_stock(self):
        """Cancelling a pending order restores product stock."""
        # Initial stock = 10, Alice places order for 4 items -> stock becomes 6
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token1.key}')
        create_res = self.client.post(self.orders_url, {'product': self.product.id, 'quantity': 4})
        order_id = create_res.data['id']

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 6)

        # Alice cancels order
        cancel_url = f'{self.orders_url}{order_id}/cancel/'
        cancel_res = self.client.post(cancel_url)
        self.assertEqual(cancel_res.status_code, status.HTTP_200_OK)

        # Stock is restored to 10
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

        # Order status is Cancelled
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, 'Cancelled')

        # Trying to cancel again fails
        second_cancel = self.client.post(cancel_url)
        self.assertEqual(second_cancel.status_code, status.HTTP_400_BAD_REQUEST)
