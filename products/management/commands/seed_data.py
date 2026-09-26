import os
from decimal import Decimal
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from orders.models import Order
from products.models import Category, Product, Review


class Command(BaseCommand):
    help = "Seed database with initial demo users, categories, products, reviews, and orders."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing orders, reviews, products, and categories before seeding for a fresh start.'
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting data seeding...")

        if options.get('clean'):
            self.stdout.write(self.style.WARNING("Cleaning existing orders, reviews, products, and categories..."))
            Order.objects.all().delete()
            Review.objects.all().delete()
            Product.objects.all().delete()
            Category.objects.all().delete()

            # Clean existing media/products directory for a truly fresh start
            media_products_dir = settings.MEDIA_ROOT / 'products'
            if media_products_dir.exists():
                for file_path in media_products_dir.iterdir():
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                        except OSError:
                            pass

            # Reset auto-increment sequence IDs back to 1
            from django.db import connection
            if connection.vendor == 'sqlite':
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM sqlite_sequence WHERE name IN "
                        "('products_product', 'products_category', 'products_review', 'orders_order');"
                    )
            elif connection.vendor == 'postgresql':
                with connection.cursor() as cursor:
                    cursor.execute("ALTER SEQUENCE products_product_id_seq RESTART WITH 1;")
                    cursor.execute("ALTER SEQUENCE products_category_id_seq RESTART WITH 1;")
                    cursor.execute("ALTER SEQUENCE products_review_id_seq RESTART WITH 1;")
                    cursor.execute("ALTER SEQUENCE orders_order_id_seq RESTART WITH 1;")

            self.stdout.write(self.style.SUCCESS("Database, auto-increment IDs & media cleaned for a fresh start!"))

        # 1. Create Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin / admin123"))
        elif admin_user.email != 'admin@example.com':
            admin_user.email = 'admin@example.com'
            admin_user.save(update_fields=['email'])
        admin_token, _ = Token.objects.get_or_create(user=admin_user)

        # 2. Create Demo Customer
        customer_user, created = User.objects.get_or_create(
            username='customer',
            defaults={
                'email': 'customer@example.com',
                'first_name': 'Demo',
                'last_name': 'Customer',
            }
        )
        if created:
            customer_user.set_password('customer123')
            customer_user.save()
            self.stdout.write(self.style.SUCCESS("Created demo customer: customer / customer123"))
        elif customer_user.email != 'customer@example.com':
            customer_user.email = 'customer@example.com'
            customer_user.save(update_fields=['email'])
        customer_token, _ = Token.objects.get_or_create(user=customer_user)

        # 3. Create Categories
        categories_data = [
            {'name': 'Smartphones', 'description': 'Latest mobile phones and handheld devices'},
            {'name': 'Laptops', 'description': 'High-performance laptops, notebooks, and ultrabooks'},
            {'name': 'Audio', 'description': 'Headphones, earbuds, speakers, and sound accessories'},
            {'name': 'Wearables', 'description': 'Smartwatches, fitness bands, and smart accessories'},
        ]

        category_objs = {}
        for cat in categories_data:
            obj, _ = Category.objects.get_or_create(
                name=cat['name'],
                defaults={'description': cat['description']}
            )
            category_objs[cat['name']] = obj

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(category_objs)} categories."))

        # 4. Create Products
        products_data = [
            {
                'name': 'iPhone 15 Pro Max',
                'category': category_objs['Smartphones'],
                'description': 'Titanium design, A17 Pro chip, 48MP main camera system, and USB-C.',
                'price': Decimal('1199.99'),
                'stock': 25,
                'image_file': 'iphone_15_pro_max.jpg',
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'category': category_objs['Smartphones'],
                'description': 'AI features, 200MP camera, built-in S Pen, and Snapdragon 8 Gen 3.',
                'price': Decimal('1299.99'),
                'stock': 18,
                'image_file': 'samsung_s24_ultra.jpg',
            },
            {
                'name': 'Google Pixel 8 Pro',
                'category': category_objs['Smartphones'],
                'description': 'Google Tensor G3, best-in-class computational photography, and 7 years of OS updates.',
                'price': Decimal('899.99'),
                'stock': 12,
                'image_file': 'google_pixel_8_pro.jpg',
            },
            {
                'name': 'MacBook Pro 16" M3 Max',
                'category': category_objs['Laptops'],
                'description': 'Apple M3 Max chip, Liquid Retina XDR display, up to 22 hours battery life.',
                'price': Decimal('2499.99'),
                'stock': 10,
                'image_file': 'macbook_pro_16.jpg',
            },
            {
                'name': 'Dell XPS 15 OLED',
                'category': category_objs['Laptops'],
                'description': '13th Gen Intel Core i7, 3.5K OLED touchscreen, NVIDIA GeForce RTX 4060 graphics.',
                'price': Decimal('1899.99'),
                'stock': 14,
                'image_file': 'dell_xps_15.jpg',
            },
            {
                'name': 'Lenovo ThinkPad X1 Carbon',
                'category': category_objs['Laptops'],
                'description': 'Ultralight carbon-fiber chassis, legendary ThinkPad keyboard, enterprise security.',
                'price': Decimal('1499.99'),
                'stock': 8,
                'image_file': 'thinkpad_x1_carbon.jpg',
            },
            {
                'name': 'Sony WH-1000XM5',
                'category': category_objs['Audio'],
                'description': 'Industry-leading noise cancellation, crystal-clear hands-free calling, 30hr battery.',
                'price': Decimal('399.99'),
                'stock': 40,
                'image_file': 'sony_wh1000xm5.jpg',
            },
            {
                'name': 'Apple AirPods Pro (2nd Gen)',
                'category': category_objs['Audio'],
                'description': 'H2 chip, Adaptive Audio, Active Noise Cancellation, and MagSafe Charging Case (USB-C).',
                'price': Decimal('249.99'),
                'stock': 50,
                'image_file': 'airpods_pro_2.jpg',
            },
            {
                'name': 'Bose QuietComfort Ultra',
                'category': category_objs['Audio'],
                'description': 'World-class noise cancellation, breakthrough spatial audio, elevated luxury materials.',
                'price': Decimal('429.99'),
                'stock': 15,
                'image_file': 'bose_qc_ultra.jpg',
            },
            {
                'name': 'Apple Watch Ultra 2',
                'category': category_objs['Wearables'],
                'description': 'Rugged titanium case, precision dual-frequency GPS, up to 36 hours of battery life.',
                'price': Decimal('799.99'),
                'stock': 20,
                'image_file': 'apple_watch_ultra_2.jpg',
            },
            {
                'name': 'Samsung Galaxy Watch 6 Classic',
                'category': category_objs['Wearables'],
                'description': 'Rotating bezel, advanced sleep coaching, body composition analysis, sapphire crystal.',
                'price': Decimal('399.99'),
                'stock': 22,
                'image_file': 'galaxy_watch_6_classic.jpg',
            },
        ]

        seed_img_dir = settings.BASE_DIR / 'products' / 'seed_images'
        created_products = []
        for p in products_data:
            prod, created = Product.objects.get_or_create(
                name=p['name'],
                defaults={
                    'category': p['category'],
                    'description': p['description'],
                    'price': p['price'],
                    'stock': p['stock'],
                }
            )
            image_filename = p.get('image_file')
            if image_filename:
                image_path = seed_img_dir / image_filename
                has_disk_image = bool(prod.image and hasattr(prod.image, 'path') and os.path.exists(prod.image.path))
                if image_path.exists() and (created or not has_disk_image or options.get('clean')):
                    with open(image_path, 'rb') as f:
                        prod.image.save(image_filename, File(f), save=True)
                    self.stdout.write(f"  -> Attached & converted seed image for '{prod.name}' -> {prod.image.name}")
            created_products.append(prod)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_products)} products with images."))

        # 5. Create Demo Orders (covering all statuses: Pending, Processing, Completed, Cancelled)
        if len(created_products) >= 4:
            demo_orders = [
                {
                    'user': customer_user,
                    'product': created_products[0],  # iPhone 15 Pro Max
                    'quantity': 1,
                    'status': 'Pending',
                },
                {
                    'user': customer_user,
                    'product': created_products[6],  # Sony WH-1000XM5
                    'quantity': 2,
                    'status': 'Processing',
                },
                {
                    'user': customer_user,
                    'product': created_products[3],  # MacBook Pro 16" M3 Max
                    'quantity': 1,
                    'status': 'Completed',
                },
                {
                    'user': customer_user,
                    'product': created_products[1],  # Samsung Galaxy S24 Ultra
                    'quantity': 1,
                    'status': 'Cancelled',
                },
                {
                    'user': admin_user,
                    'product': created_products[7],  # Apple AirPods Pro
                    'quantity': 1,
                    'status': 'Completed',
                },
            ]

            seeded_order_count = 0
            for item in demo_orders:
                prod = item['product']
                qty = item['quantity']
                total = prod.price * qty
                Order.objects.get_or_create(
                    user=item['user'],
                    product=prod,
                    status=item['status'],
                    defaults={
                        'quantity': qty,
                        'total_price': total,
                    }
                )
                seeded_order_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Seeded {seeded_order_count} sample orders across all statuses (Pending, Processing, Completed, Cancelled)."
            ))

        # 6. Create Reviews (synced strictly with Completed orders)
        if len(created_products) >= 8:
            # Customer reviews MacBook Pro 16" (Order #3 is Completed)
            review1, created = Review.objects.get_or_create(
                product=created_products[3],
                user=customer_user,
                defaults={
                    'rating': 4,
                    'comment': 'Outstanding build quality, battery life, and Apple M3 Max performance!'
                }
            )
            if not created and review1.rating != 4:
                review1.rating = 4
                review1.save(update_fields=['rating'])
            # Admin reviews Apple AirPods Pro (Order #5 is Completed)
            Review.objects.get_or_create(
                product=created_products[7],
                user=admin_user,
                defaults={
                    'rating': 5,
                    'comment': 'Best noise cancelling earbuds with seamless Apple ecosystem integration.'
                }
            )
            self.stdout.write(self.style.SUCCESS("Seeded sample product reviews (synced with Completed orders)."))

        self.stdout.write(self.style.SUCCESS("\nData seeding completed successfully!"))
        self.stdout.write("--------------------------------------------------")
        self.stdout.write(f"Admin User:    admin    / admin123    (Token: {admin_token.key})")
        self.stdout.write(f"Customer User: customer / customer123 (Token: {customer_token.key})")
        self.stdout.write("--------------------------------------------------")
