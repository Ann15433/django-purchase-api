import csv
import json
import os
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from core.models import Supplier, Product

class Command(BaseCommand):
    help = 'Импортирует товары из CSV-файла: python manage.py import_products путь/к/файлу.csv'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV-файлу для импорта')

    def handle(self, *args, **options):
        csv_path = options['csv_file']

        if not os.path.isfile(csv_path):
            raise CommandError(f'Файл не найден: {csv_path}')

        created_count = 0
        updated_count = 0
        error_count = 0

        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # start=2, т.к. 1-я строка — заголовок
                try:
                    supplier_name = row['supplier_name'].strip()
                    name = row['name'].strip()
                    description = row.get('description', '').strip()
                    price_str = row['price'].strip()
                    sku = row['sku'].strip()
                    stock_quantity_str = row.get('stock_quantity', '0').strip()
                    extra_fields_str = row.get('extra_fields', '{}').strip() or '{}'

                    # Парсим JSON extra_fields
                    try:
                        extra_fields = json.loads(extra_fields_str)
                    except json.JSONDecodeError as e:
                        self.stdout.write(self.style.ERROR(f'Строка {row_num}: неверный JSON в extra_fields: {e}'))
                        error_count += 1
                        continue

                    # Цена и остаток — числа
                    try:
                        price = float(price_str)
                        stock_quantity = int(stock_quantity_str) if stock_quantity_str else 0
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f'Строка {row_num}: ошибка числа (price/stock): {e}'))
                        error_count += 1
                        continue

                    supplier, _ = Supplier.objects.get_or_create(
                        name=supplier_name,
                        defaults={'is_active': True}
                    )

                    product, created = Product.objects.update_or_create(
                        sku=sku,
                        defaults={
                            'name': name,
                            'description': description,
                            'supplier': supplier,
                            'price': price,
                            'stock_quantity': stock_quantity,
                            'is_active': True,
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                except KeyError as e:
                    self.stdout.write(self.style.ERROR(f'Строка {row_num}: отсутствует колонка: {e}'))
                    error_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Строка {row_num}: непредвиденная ошибка: {e}'))
                    error_count += 1

        self.stdout.write(self.style.SUCCESS('Импорт завершён!'))
        self.stdout.write(f'Создано товаров: {created_count}')
        self.stdout.write(f'Обновлено товаров: {updated_count}')
        self.stdout.write(f'Ошибок: {error_count}')
