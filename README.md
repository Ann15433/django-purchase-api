# Django Purchase API

Дипломный проект: REST API для автоматизации закупок и оформления заказов.

## Функционал
- Создание заказа через POST-запрос.
- Привязка товара по ID (защита от опечаток в названиях).
- Автоматический расчёт итоговой стоимости на основе цены из БД.
- Отправка email-уведомления пользователю.
- Команда управления `import_products` для загрузки товаров из CSV.

## Технологии
- Python, Django, Django REST Framework, SQLite.

## Установка и запуск

```bash
git clone https://github.com/Ann15433/django-purchase-api.git
cd django-purchase-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
