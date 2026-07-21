from django.conf import settings
from django.db import models
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('paid', 'Оплачен'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    delivery_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        product_name = self.product.name if self.product else "Unknown"
        return f'{self.quantity} x {product_name}'
