from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from orders.models import Order
from products.models import Category, Product, Review


class RigorousE2ETests(APITestCase):
    """
    Comprehensive, rigorous end-to-end integration test suite.
    Validates all edge cases, security boundaries, isolation rules,
    concurrency scenarios, filtering combinations, and error responses.
    """

    def setUp(self):
        # 1. Setup Users
        self.admin = User.objects.create_superuser(
            username='admin_boss',
            email='admin_boss@test.com',
            password='AdminPassword123!'
        )
        self.admin_token = Token.objects.create(user=self.admin)

        self.customer1 = User.objects.create_user(
            username='customer_one',
            email='c1@test.com',
            password='Customer1Password!'
        )
        self.c1_token = Token.objects.create(user=self.customer1)

        self.customer2 = User.objects.create_user(
            username='customer_two',
            email='c2@test.com',
            password='Customer2Password!'
        )
        self.c2_token = Token.objects.create(user=self.customer2)

        # 2. Setup Categories
        self.cat_phones = Category.objects.create(
            name='Smartphones',
            description='Handheld mobile devices'
        )
        self.cat_laptops = Category.objects.create(
            name='Laptops',
            description='Portable personal computers'
        )

        # 3. Setup Products
        self.p_iphone = Product.objects.create(
            category=self.cat_phones,
            name='iPhone 15 Pro',
            description='Apple flagship smartphone with A17 Pro titanium design',
            price=Decimal('999.00'),
            stock=5
        )
        self.p_galaxy = Product.objects.create(
            category=self.cat_phones,
            name='Samsung Galaxy S24',
            description='Samsung Android flagship phone with AI',
            price=Decimal('799.00'),
            stock=10
        )
        self.p_pixel = Product.objects.create(
            category=self.cat_phones,
            name='Google Pixel 8',
            description='Google pure Android phone with Tensor G3',
            price=Decimal('699.00'),
            stock=0  # Out of stock
        )
        self.p_macbook = Product.objects.create(
            category=self.cat_laptops,
            name='MacBook Air M3',
            description='Apple lightweight laptop computer',
            price=Decimal('1099.00'),
            stock=8
        )
        self.p_dell = Product.objects.create(
            category=self.cat_laptops,
            name='Dell XPS 13',
            description='Windows ultra-portable laptop computer',
            price=Decimal('1199.00'),
            stock=3
        )

    # ---------------------------------------------------------
    # SUITE 1: AUTHENTICATION & SECURITY BOUNDARIES
    # ---------------------------------------------------------

    def test_01_registration_strict_validations(self):
        """Test registration edge cases: email format, username uniqueness, password confirmation."""
        # Mismatched passwords
        res = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Password123!',
            'password2': 'Mismatch123!'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', res.data)

        # Duplicate username (case-insensitive check)
        res = self.client.post('/api/auth/register/', {
            'username': 'CUSTOMER_ONE',
            'email': 'different@test.com',
            'password': 'Password123!',
            'password2': 'Password123!'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', res.data)

        # Duplicate email
        res = self.client.post('/api/auth/register/', {
            'username': 'brandnewuser',
            'email': 'c1@test.com',
            'password': 'Password123!',
            'password2': 'Password123!'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data)

        # Valid registration
        res = self.client.post('/api/auth/register/', {
            'username': 'valid_user',
            'email': 'valid@test.com',
            'password': 'ValidPassword123!',
            'password2': 'ValidPassword123!',
            'first_name': 'Valid',
            'last_name': 'User'
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', res.data)
        self.assertTrue(Token.objects.filter(key=res.data['token']).exists())

    def test_02_login_and_logout_lifecycle(self):
        """Test full login, profile retrieval, and logout token invalidation cycle."""
        # 1. Login with bad credentials
        res = self.client.post('/api/auth/login/', {
            'username': 'customer_one',
            'password': 'WrongPassword!'
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # 2. Login with valid credentials
        res = self.client.post('/api/auth/login/', {
            'username': 'customer_one',
            'password': 'Customer1Password!'
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        token_key = res.data['token']
        self.assertEqual(token_key, self.c1_token.key)

        # 3. Access profile with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token_key}')
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'customer_one')

        # 4. Update profile
        res = self.client.patch('/api/auth/profile/', {'first_name': 'UpdatedFirst'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.customer1.refresh_from_db()
        self.assertEqual(self.customer1.first_name, 'UpdatedFirst')

        # 5. Logout
        res = self.client.post('/api/auth/logout/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # 6. Verify token is deleted in DB
        self.assertFalse(Token.objects.filter(key=token_key).exists())

        # 7. Subsequent request with invalidated token must fail with 401
        res = self.client.get('/api/auth/profile/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_03_invalid_and_malformed_auth_headers(self):
        """Test API behavior with corrupt, nonexistent, or malformed tokens."""
        # Non-existent token
        self.client.credentials(HTTP_AUTHORIZATION='Token 0000000000000000000000000000000000000000')
        res = self.client.get('/api/orders/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # Malformed header
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidformat')
        res = self.client.get('/api/orders/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------------------------------------------------------
    # SUITE 2: CATEGORY & PRODUCT PERMISSIONS & INTEGRITY
    # ---------------------------------------------------------

    def test_04_category_rbac_permissions(self):
        """Verify that only staff/admin can modify categories, while public can read."""
        # Public read
        res = self.client.get('/api/categories/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Customer try create
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.c1_token.key}')
        res = self.client.post('/api/categories/', {'name': 'Tablets'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin create
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        res = self.client.post('/api/categories/', {'name': 'Tablets', 'description': 'iPad and Android tablets'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        tab_id = res.data['id']

        # Duplicate category name
        res = self.client.post('/api/categories/', {'name': 'Tablets'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Customer try delete
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.c1_token.key}')
        res = self.client.delete(f'/api/categories/{tab_id}/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        # Admin delete
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        res = self.client.delete(f'/api/categories/{tab_id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_05_product_rbac_and_data_integrity(self):
        """Verify product creation rules, price/stock bounds, and category associations."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')

        # Reject negative price
        res = self.client.post('/api/products/', {
            'name': 'Bad Product',
            'price': '-50.00',
            'stock': 10,
            'category': self.cat_phones.id
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Reject zero price
        res = self.client.post('/api/products/', {
            'name': 'Free Product',
            'price': '0.00',
            'stock': 10,
            'category': self.cat_phones.id
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Reject negative stock
        res = self.client.post('/api/products/', {
            'name': 'Negative Stock',
            'price': '100.00',
            'stock': -5,
            'category': self.cat_phones.id
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Reject non-existent category
        res = self.client.post('/api/products/', {
            'name': 'No Category Product',
            'price': '100.00',
            'stock': 5,
            'category': 99999
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Successful creation with category_name in response
        res = self.client.post('/api/products/', {
            'name': 'iPad Air',
            'description': 'M2 chip tablet',
            'price': '599.99',
            'stock': 15,
            'category': self.cat_phones.id
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['category_name'], 'Smartphones')

    # ---------------------------------------------------------
    # SUITE 3: ADVANCED SEARCHING, FILTERING, ORDERING, PAGINATION
    # ---------------------------------------------------------

    def test_06_product_search_rigorous(self):
        """Test searching by product name and description case-insensitively."""
        # Search 'iphone'
        res = self.client.get('/api/products/?search=iphone')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in res.data['results']]
        self.assertIn('iPhone 15 Pro', names)
        self.assertNotIn('Samsung Galaxy S24', names)

        # Search 'computer' (matches description of MacBook and Dell XPS)
        res = self.client.get('/api/products/?search=computer')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in res.data['results']]
        self.assertIn('MacBook Air M3', names)
        self.assertIn('Dell XPS 13', names)
        self.assertNotIn('iPhone 15 Pro', names)

        # Search non-matching term
        res = self.client.get('/api/products/?search=xyznonexistent')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 0)

    def test_07_product_filters_and_combinations(self):
        """Test category filter (by ID and Name), price ranges, and multi-filter combinations."""
        # 1. Filter by category ID
        res = self.client.get(f'/api/products/?category={self.cat_phones.id}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 3)

        # 2. Filter by category Name
        res = self.client.get('/api/products/?category=Laptops')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

        # 3. Filter by price exact
        res = self.client.get('/api/products/?price=799.00')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['name'], 'Samsung Galaxy S24')

        # 4. Filter by price range
        res = self.client.get('/api/products/?min_price=700&max_price=1000')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in res.data['results']]
        self.assertIn('iPhone 15 Pro', names)
        self.assertIn('Samsung Galaxy S24', names)
        self.assertNotIn('Google Pixel 8', names)
        self.assertNotIn('MacBook Air M3', names)

        # 5. Combined filter: category + min_price + ordering
        res = self.client.get(f'/api/products/?category={self.cat_phones.id}&min_price=750&ordering=-price')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['name'], 'iPhone 15 Pro')
        self.assertEqual(results[1]['name'], 'Samsung Galaxy S24')

    def test_08_ordering_and_custom_pagination(self):
        """Test price ordering directions and pagination metadata."""
        # Ascending price
        res = self.client.get('/api/products/?ordering=price')
        prices = [Decimal(p['price']) for p in res.data['results']]
        self.assertEqual(prices, sorted(prices))

        # Descending price
        res = self.client.get('/api/products/?ordering=-price')
        prices_desc = [Decimal(p['price']) for p in res.data['results']]
        self.assertEqual(prices_desc, sorted(prices_desc, reverse=True))

        # Pagination: 2 items per page
        res = self.client.get('/api/products/?page=1&page_size=2')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
        self.assertEqual(res.data['count'], 5)
        self.assertEqual(res.data['total_pages'], 3)
        self.assertEqual(res.data['current_page'], 1)
        self.assertIsNotNone(res.data['next'])
        self.assertIsNone(res.data['previous'])

        # Page 2
        res2 = self.client.get(res.data['next'])
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res2.data['results']), 2)
        self.assertEqual(res2.data['current_page'], 2)

    # ---------------------------------------------------------
    # SUITE 4: ORDER CREATION, STOCK CONCURRENCY & ISOLATION
    # ---------------------------------------------------------

    def test_09_order_stock_validation_and_decrement(self):
        """Test order creation, exact stock deduction, and out-of-stock rejection."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.c1_token.key}')

        # 1. Out-of-stock product rejection
        res = self.client.post('/api/orders/', {
            'product': self.p_pixel.id,  # stock = 0
            'quantity': 1
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', res.data)

        # 2. Exceeding available stock rejection
        res = self.client.post('/api/orders/', {
            'product': self.p_iphone.id,  # stock = 5
            'quantity': 6
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.p_iphone.refresh_from_db()
        self.assertEqual(self.p_iphone.stock, 5)  # Untouched

        # 3. Valid order placing
        res = self.client.post('/api/orders/', {
            'product': self.p_iphone.id,
            'quantity': 2
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(res.data['total_price']), Decimal('1998.00'))  # 999 * 2
        self.assertEqual(res.data['product_name'], 'iPhone 15 Pro')

        # Verify stock decreased from 5 to 3
        self.p_iphone.refresh_from_db()
        self.assertEqual(self.p_iphone.stock, 3)

        # 4. Another order exhausting remaining stock
        res2 = self.client.post('/api/orders/', {
            'product': self.p_iphone.id,
            'quantity': 3
        })
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.p_iphone.refresh_from_db()
        self.assertEqual(self.p_iphone.stock, 0)

        # 5. Subsequent order fails because stock is now 0
        res3 = self.client.post('/api/orders/', {
            'product': self.p_iphone.id,
            'quantity': 1
        })
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_10_strict_user_order_isolation(self):
        """Ensure Customer 1 cannot see or access Customer 2's orders under any circumstances."""
        # Create Order for Customer 1
        order_c1 = Order.objects.create(
            user=self.customer1,
            product=self.p_galaxy,
            quantity=1,
            total_price=Decimal('799.00')
        )

        # Create Order for Customer 2
        order_c2 = Order.objects.create(
            user=self.customer2,
            product=self.p_macbook,
            quantity=1,
            total_price=Decimal('1099.00')
        )

        # Customer 1 lists orders
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.c1_token.key}')
        res = self.client.get('/api/orders/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        order_ids = [o['id'] for o in res.data['results']]
        self.assertIn(order_c1.id, order_ids)
        self.assertNotIn(order_c2.id, order_ids)

        # Customer 1 tries to access Customer 2's single order detail
        res = self.client.get(f'/api/orders/{order_c2.id}/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # Customer 1 tries to cancel Customer 2's order
        res = self.client.post(f'/api/orders/{order_c2.id}/cancel/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        # Admin can view all orders
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        res = self.client.get('/api/orders/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 2)

    def test_11_order_cancellation_and_inventory_refund(self):
        """Verify cancelling a pending order correctly refunds inventory stock."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.c1_token.key}')

        # Buy 3 Dell XPS (initial stock = 3)
        res = self.client.post('/api/orders/', {
            'product': self.p_dell.id,
            'quantity': 3
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        order_id = res.data['id']

        self.p_dell.refresh_from_db()
        self.assertEqual(self.p_dell.stock, 0)

        # Cancel order
        res_cancel = self.client.post(f'/api/orders/{order_id}/cancel/')
        self.assertEqual(res_cancel.status_code, status.HTTP_200_OK)

        # Stock must be refunded back to 3
        self.p_dell.refresh_from_db()
        self.assertEqual(self.p_dell.stock, 3)

        # Verify order status changed to Cancelled
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, 'Cancelled')

        # Double cancellation must be rejected
        res_double_cancel = self.client.post(f'/api/orders/{order_id}/cancel/')
        self.assertEqual(res_double_cancel.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------
    # SUITE 5: REVIEWS, RATINGS & DOCUMENTATION ENDPOINTS
    # ---------------------------------------------------------

    def test_12_reviews_ratings_dynamic_calculation(self):
        """Verify review submissions, one-review-per-user constraint, and rating averaging."""
        # Create Completed orders for customer1 and customer2 on Galaxy S24
        Order.objects.create(
            user=self.customer1,
            product=self.p_galaxy,
            quantity=1,
            total_price=self.p_galaxy.price,
            status='Completed'
        )
        Order.objects.create(
            user=self.customer2,
            product=self.p_galaxy,
            quantity=1,
            total_price=self.p_galaxy.price,
            status='Completed'
        )

        # Customer 1 reviews Galaxy S24 with rating 4
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.c1_token.key}')
        res1 = self.client.post(f'/api/products/{self.p_galaxy.id}/reviews/', {
            'rating': 4,
            'comment': 'Good phone, battery could be better.'
        })
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # Customer 2 reviews Galaxy S24 with rating 5
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.c2_token.key}')
        res2 = self.client.post(f'/api/products/{self.p_galaxy.id}/reviews/', {
            'rating': 5,
            'comment': 'Flawless performance and camera!'
        })
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

        # Customer 2 tries to review again (duplicate)
        res_dup = self.client.post(f'/api/products/{self.p_galaxy.id}/reviews/', {
            'rating': 3,
            'comment': 'Second thought'
        })
        self.assertEqual(res_dup.status_code, status.HTTP_400_BAD_REQUEST)

        # Check product detail view reflects average rating: (4 + 5) / 2 = 4.5
        res_prod = self.client.get(f'/api/products/{self.p_galaxy.id}/')
        self.assertEqual(res_prod.status_code, status.HTTP_200_OK)
        self.assertEqual(res_prod.data['average_rating'], 4.5)
        self.assertEqual(res_prod.data['total_reviews'], 2)
        self.assertEqual(len(res_prod.data['reviews']), 2)

    def test_13_openapi_schema_and_documentation_views(self):
        """Verify Swagger UI, ReDoc, Schema JSON, and API Root endpoints are responsive."""
        # API Root index
        res = self.client.get('/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('endpoints', res.data)

        # OpenAPI schema
        res = self.client.get('/api/schema/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Swagger UI
        res = self.client.get('/api/docs/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # ReDoc
        res = self.client.get('/api/redoc/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
