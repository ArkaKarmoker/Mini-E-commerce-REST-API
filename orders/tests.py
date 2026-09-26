from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from products.models import Category, Product
from .models import Order


class OrderAPITests(APITestCase):
    """
    Core test suite for Order placement, Stock validation, User isolation, and Stock refund.
    """

    def setUp(self):
        self.buyer1 = User.objects.create_user(
            username='buyer1',
            email='buyer1@example.com',
            password='Password123!'
        )
        self.b1_token = Token.objects.create(user=self.buyer1)

        self.buyer2 = User.objects.create_user(
            username='buyer2',
            email='buyer2@example.com',
            password='Password123!'
        )
        self.b2_token = Token.objects.create(user=self.buyer2)

        self.category = Category.objects.create(name='Electronics', description='Gadgets')
        self.product = Product.objects.create(
            category=self.category,
            name='Wireless Headphones',
            description='Noise cancelling headphones',
            price=Decimal('200.00'),
            stock=10
        )

    def test_create_order_deducts_stock_and_calculates_total(self):
        """1. Place an order: auto-calculates total price and deducts stock atomically."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.b1_token.key}')
        payload = {'product': self.product.id, 'quantity': 3}
        response = self.client.post('/api/orders/', payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'Pending')
        self.assertEqual(Decimal(str(response.data['total_price'])), Decimal('600.00'))

        # Stock deducted from 10 to 7
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 7)

    def test_create_order_insufficient_stock_rejected(self):
        """2. Stock validation rejects orders exceeding current inventory (400 Bad Request)."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.b1_token.key}')
        payload = {'product': self.product.id, 'quantity': 50}  # stock is 10
        response = self.client.post('/api/orders/', payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Stock remains intact
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)

    def test_order_user_isolation(self):
        """3. User isolation: customers can view only their own orders."""
        order1 = Order.objects.create(
            user=self.buyer1, product=self.product, quantity=1,
            total_price=Decimal('200.00'), status='Pending'
        )
        order2 = Order.objects.create(
            user=self.buyer2, product=self.product, quantity=2,
            total_price=Decimal('400.00'), status='Pending'
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.b1_token.key}')
        # List orders returns only buyer1's order
        list_resp = self.client.get('/api/orders/')
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)
        results = list_resp.data.get('results', list_resp.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], order1.id)

        # Accessing buyer2's order returns 404
        detail_resp = self.client.get(f'/api/orders/{order2.id}/')
        self.assertEqual(detail_resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_restores_stock(self):
        """4. Cancelling a pending order marks it Cancelled and refunds product stock."""
        self.product.stock = 8
        self.product.save(update_fields=['stock'])

        order = Order.objects.create(
            user=self.buyer1, product=self.product, quantity=2,
            total_price=Decimal('400.00'), status='Pending'
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.b1_token.key}')
        response = self.client.post(f'/api/orders/{order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        order.refresh_from_db()
        self.assertEqual(order.status, 'Cancelled')

        # Stock refunded (8 + 2 = 10)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 10)
