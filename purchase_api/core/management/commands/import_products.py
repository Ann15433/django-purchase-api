import csv
from django.core.management.base import BaseCommand, CommandError
from core.models import Product

class Command(BaseCommand):
    help = 'Импортирует товары из CSV-файла. Ожидаемые колонки: name, price'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Путь к CSV-файлу для импорта')

    def handle(self, *args, **options):
        csv_path = options['csv_file']

        if not csv_path:
            raise CommandError('Укажите путь к CSV-файлу: python manage.py import_products путь/к/файлу.csv')

        if not csv_path.endswith('.csv'):
            self.stdout.write(self.style.WARNING('Файл не имеет расширения .csv, но будет обработан.'))

        if not csv_path or not csv_path.strip():
            raise CommandError('Путь к файлу не может быть пустым.')

        # Проверка существования файла
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                pass
        except FileNotFoundError:
            raise CommandError(f'Файл не найден: {csv_path}')
        except Exception as e:
            raise CommandError(f'Не удалось открыть файл: {e}')

        created_count = 0
        updated_count = 0
        error_count = 0

        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            # Проверка, есть ли нужные колонки
            if reader.fieldnames is None:
                raise CommandError('CSV-файл пуст или не содержит заголовков.')

            required_fields = {'name', 'price'}
            available_fields = set(reader.fieldnames)
            missing_fields = required_fields - available_fields

            if missing_fields:
                raise CommandError(
                    f'В CSV-файле отсутствуют обязательные колонки: {", ".join(missing_fields)}. '
                    f'Доступные колонки: {", ".join(available_fields)}'
                )

            for row_num, row in enumerate(reader, start=2):  # start=2, т.к. 1-я строка — заголовок
                name = row.get('name', '').strip()
                price_str = row.get('price', '').strip()

                # Пропускаем строки без имени или цены
                if not name or not price_str:
                    self.stdout.write(self.style.WARNING(f'Строка {row_num}: пропущена (нет name или price)'))
                    error_count += 1
                    continue

                try:
                    price = float(price_str)
                except ValueError:
                    self.stdout.write(self.style.ERROR(f'Строка {row_num}: цена "{price_str}" не является числом'))
                    error_count += 1
                    continue

                product, created = Product.objects.update_or_create(
                    name=name,
                    defaults={'price': price}
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS('Импорт завершён!'))
        self.stdout.write(f'Создано товаров: {created_count}')
        self.stdout.write(f'Обновлено товаров: {updated_count}')
        self.stdout.write(f'Пропущено/ошибочных строк: {error_count}')
