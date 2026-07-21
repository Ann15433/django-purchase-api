from django.core.mail import send_mail
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, Product
from .serializers import OrderSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CreateOrderView(APIView):
    def post(self, request, *args, **kwargs):
        # Получаем ID товара из запроса (теперь это число, например 1)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        if product_id is None:
            return Response(
                {'error': 'Поле "product" (ID товара) обязательно'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Ищем товар по ID. Если передали не число или товара нет — сработает except
        try:
            product = Product.objects.get(id=product_id)
            price = product.price
        except (Product.DoesNotExist, ValueError):
            # Если товара с таким ID нет или передали не число, ставим заглушку
            price = Decimal('50000.00')
            product = None

        total_price = Decimal(price) * Decimal(int(quantity))

        current_user = request.user

        # Если пользователь не авторизован, берем первого пользователя из базы для теста
        if not current_user or not current_user.is_authenticated:
            try:
                current_user = User.objects.first()
                print(f"Для теста используется пользователь: {current_user.username}")
            except User.DoesNotExist:
                return Response(
                    {'error': 'В базе нет ни одного пользователя. Создайте пользователя в админке.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        order = Order.objects.create(
            user=current_user,
            status='new',
            total_price=total_price,
            delivery_address=request.data.get('delivery_address', ''),
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price,
        )

        user_email = current_user.email if current_user.is_authenticated else None

        if user_email:
            try:
                send_mail(
                    subject=f'Подтверждение заказа №{order.id}',
                    message=(
                        f'Ваш заказ №{order.id} успешно создан.\n'
                        f'Товар: {product.name if product else "Неизвестный товар"}, количество: {quantity}\n'
                        f'Итого: {total_price} руб.\n'
                        f'Статус: {order.status}'
                    ),
                    from_email='no-reply@purchase-api.local',
                    recipient_list=[user_email],
                )
                print(f'Письмо для заказа {order.id} отправлено на {user_email}')
            except Exception as e:
                print(f'Ошибка отправки письма (игнорируем для теста): {e}')
        else:
            print('Не удалось отправить письмо: у выбранного пользователя нет email')

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

