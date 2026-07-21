from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.ListSerializer(child=OrderItemSerializer(), read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'created_at',
            'total_price',
            'delivery_address',
            'items',
        ]
        read_only_fields = ['created_at', 'total_price']
