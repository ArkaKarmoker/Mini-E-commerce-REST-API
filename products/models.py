import os
from decimal import Decimal
from io import BytesIO
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from PIL import Image


class Category(models.Model):
    """
    Category model for grouping products.
    """
    name = models.CharField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model representing items in the e-commerce store.
    """
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), message="Price must be greater than 0.")]
    )
    stock = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0, message="Stock cannot be negative.")]
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.name} (${self.price})"

    def save(self, *args, **kwargs):
        """
        Automatically convert and optimize uploaded images to WebP format.
        """
        if self.image:
            name_lower = self.image.name.lower()
            if not name_lower.endswith('.webp'):
                try:
                    self.image.open()
                    img = Image.open(self.image)
                    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                        img = img.convert('RGBA')
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')

                    output = BytesIO()
                    img.save(output, format='WEBP', quality=85, optimize=True)
                    output.seek(0)

                    old_path = self.image.path if hasattr(self.image, 'path') and os.path.exists(self.image.path) else None

                    base_name = os.path.splitext(os.path.basename(self.image.name))[0]
                    webp_name = f"{base_name}.webp"
                    self.image.save(webp_name, ContentFile(output.getvalue()), save=False)

                    if old_path and os.path.exists(old_path) and not old_path.lower().endswith('.webp'):
                        try:
                            os.remove(old_path)
                        except OSError:
                            pass
                except Exception:
                    pass
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        """Calculates the average rating from all reviews for this product."""
        avg = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg, 2) if avg is not None else 0.0

    @property
    def total_reviews(self):
        """Returns the total number of reviews."""
        return self.reviews.count()


class Review(models.Model):
    """
    Review and rating model for products (optional feature).
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Rating must be at least 1."),
            MaxValueValidator(5, message="Rating cannot be more than 5.")
        ]
    )
    comment = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def clean(self):
        super().clean()
        if self.user_id and self.product_id:
            from orders.models import Order
            from django.core.exceptions import ValidationError
            has_completed_order = Order.objects.filter(
                user_id=self.user_id,
                product_id=self.product_id,
                status='Completed'
            ).exists()
            if not has_completed_order:
                raise ValidationError(
                    "You can only review a product if you have purchased it and the order status is 'Completed'."
                )

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"
