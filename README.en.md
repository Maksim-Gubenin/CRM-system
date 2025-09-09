# CRM Backoffice System

## Description

Web application for automating customer relationship management. The system provides tools for working with leads, contracts, advertising campaigns, and business processes.

## Technologies

#### Backend

- Python 3.12

- Django 5.2.4

- Django REST Framework

- PostgreSQL 17.5

- Redis 7.4

#### Frontend

- HTML5 + CSS3

- Custom CSS

#### Infrastructure

- Docker

- Docker Compose

- Nginx

- Gunicorn

- Poetry

## Getting Started

### Requirements

- Docker 20.10+

- Docker Compose 2.0+

## Quick Start

### Download from repository

```bash
git clone <repository-url>
cd CRM-system
```

### Configure environment variables

```bash
cp .env.template .env
```

### Start the application
```bash
docker-compose up -d --build
```

### Run migrations

```bash
docker-compose exec web python manage.py migrate
```

### Create superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### Application access:
Main site: http://localhost/

Admin panel: http://localhost/admin/


## Environment Variables .env

### Security

- DJANGO_SECRET_KEY=your-very-secure-secret-key-change-this

- DJANGO_DEBUG=0

- ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

### Database

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

### Security

CSRF_TRUSTED_ORIGINS=http://localhost

## Development
Create superuser
```bash
docker-compose exec web python manage.py createsuperuser
```

### Start application
```bash
docker-compose up --build
```

### Database migrations
```bash
docker-compose exec web python manage.py migrate
```

### Create administrator
```bash
docker-compose exec web python manage.py createsuperuser
```

### Collect static files
```bash
docker-compose exec web python manage.py collectstatic
```

### Django shell
```bash
docker-compose exec web python manage.py shell
```

### View logs
```bash
docker-compose logs web
docker-compose logs nginx
```

## Testing

### All tests
```bash
docker-compose exec web python manage.py test
```

### With code coverage
```bash
poetry run coverage run --source=. manage.py test --verbosity=2
poetry run coverage report
```

## Docker Services

- web - Django application (Gunicorn)

- db - PostgreSQL database

- redis - Redis cache and sessions

- nginx - Web server and static files

## Project Team
Maxim Gubenin - Full Stack Developer
Email: maksimgubenin@mail.ru

## Support

Bug reports: create issues in the repository

Suggestions: submit pull requests

Questions: write to email