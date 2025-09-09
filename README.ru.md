# CRM Backoffice System


## Описание

Веб-приложение для автоматизации управления клиентскими отношениями. Система предоставляет инструменты для работы с лидами, контрактами, рекламными кампаниями и бизнес-процессами.

## Технологии

#### Backend

- Python 3.12

- Django 5.2.4

- Django REST Framework

- PostgreSQL 17.5

- Redis 7.4

#### Frontend

- HTML5 + CSS3

- Кастомный CSS

#### Инфраструктура

- Docker 

- Docker Compose

- Nginx

- Gunicorn

- Poetry

## Начало работы

### Требования

- Docker 20.10+

- Docker Compose 2.0+

## Быстрый запуск

### Скачать из репозитория

```bash
git clone <repository-url> 
cd CRM-system
```

### Настройте переменные окружения
```bash
cp .env.template .env
```

### Запустите приложение
```bash
docker-compose up -d --build
```

### Выполните миграции
```bash
docker-compose exec web python manage.py migrate
```


### Создайте суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```


### Доступ к приложению:

Основной сайт: http://localhost/

Админ панель: http://localhost/admin/

## Переменные окружения .env

### Безопасность
- DJANGO_SECRET_KEY=your-very-secure-secret-key-change-this
- DJANGO_DEBUG=0
- ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

### База данных
- DB_NAME=crm_system
- DB_USER=web_app
- DB_PASSWORD=your-database-password
- DB_HOST=db
- DB_PORT=5432

### Email
- EMAIL_HOST=smtp.gmail.com
- EMAIL_PORT=587
- EMAIL_USE_TLS=1
- EMAIL_HOST_USER=your-email@gmail.com
- EMAIL_HOST_PASSWORD=your-app-password

### Безопасность
CSRF_TRUSTED_ORIGINS=http://localhost

## Разработка

### Создайте суперпользователя
```bash
docker-compose exec web python manage.py createsuperuser
```

### Запуск приложения
```bash
docker-compose up --build
```

### Миграции базы данных
```bash
docker-compose exec web python manage.py migrate
```

### Создание администратора
```bash
docker-compose exec web python manage.py createsuperuser
```


### Сбор статических файлов
```bash
docker-compose exec web python manage.py collectstatic
```

### Сбор статических файлов
```bash
docker-compose exec web python manage.py shell
```

### Просмотр логов
```bash
docker-compose logs web
docker-compose logs nginx
```

## Тестирование

### Все тесты
```bash
docker-compose exec web python manage.py test
```

### ВС покрытием кода
```bash
poetry run coverage run --source=. manage.py test --verbosity=2
poetry run coverage report
```

## Docker сервисы

- web - Django приложение (Gunicorn)

- db - PostgreSQL база данных

- redis - Redis кэш и сессии

- nginx - Веб-сервер и статика

## Команда проекта

Максим Губенин - Full Stack Developer
Email: maksimgubenin@mail.ru

## Поддержка

Баг-репорты: создавайте issue в репозитории

Предложения: отправляйте pull request

Вопросы: пишите на email