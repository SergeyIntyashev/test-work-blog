<h2 align="center">Blog API by Django </h2>

## Описание тестового задания
Реализовать сервис, который принимает и отвечает на HTTP-запросы, для работы с
блогами.

**Модели**
- Блог (Blogs)
- Теги (Tags)
- Пост (Posts)
- Комментарий (Comments)
- Пользователь (CustomUser)

**Возможности пользователя**
- создавать блог (POST ``/api/blogs``)
- добавлять в свой блог авторов (PATCH ``/api/blogs/{blog_id}/add-authors``)
- публиковать в блог посты (POST ``/api/posts``)
- добавлять комментарии к посту (POST ``/api/posts/{post_id}/add-comment``)
- добавлять блог в "мои подписки" (PATCH ``/api/blogs/{blog_id}/subscribe``)

Администратор может создавать, редактировать и удалять любые сущности

**Страницы (отдельные URL)**
- главная - последние N постов со всех блогов (GET ``/api/posts``)
- "Список блогов" - последние N блогов по дате обновления (GET ``/api/blogs``)
- "Посты блога" - последние N постов по дате публикации 
(GET ``/api/blogs/{blog_id}/posts``)
- "Мои посты" - опубликованые пользователем (GET ``/api/posts/my``)
- "Мои подписки" - блоги, на которые подписан пользователь
(GET ``/api/blogs/favorites``)
- CRUD на блоги и посты (``/api/blogs`` и ``/api/posts``)

**На всех страницах блогов/постов реализовано поведение:**
- пагинация (выводится по 10 записей)
- поиск по названию (title) и username автора
- фильтры по дате создания (created_at), по тегам (tags)
- сортировка по названию (title), дате создания (created_at), 
лайкам (likes, только для постов)

## Описание проекта

**Стек:**
- Django
- Django REST Framework
- Django REST Framework Simple JWT 
(для аутентификации по JWT токену)
- Django ORM
- PostgreSQL

Все методы API задокументированы с помощью swagger. 
Для получения информации по API необходимо перейти на ``/swagger/``.

**Аутентификация/авторизация:**
- Для создания пользователя необходимо отправить (POST) запрос на 
``/auth/sign-in`` c username и password. 
- Для авторизации пользователя необходимо отправить (POST) запрос на 
``/auth/login`` c username и password, в ответ будет получены access и refresh
токены.
- Для выхода необходимо отправить (POST) на ``/auth/logout`` с refresh токеном.
- Для отправки авторизованных запросов необходимо добавлять к запросу
заголовок Authorization со значением "Bearer {access token}".

## Подготовительные действия
Переименовать файл в корне приложения .env.example на .env и изменить
настройки, если потребуется. 

## Запуск приложения

**Запуск с docker:**

#### 1) Создание образа

    docker-compose build

##### 2) Запустить контейненр

    docker-compose up
    
##### 3) Создать суперпользователя

    docker exec -it blog_app python manage.py createsuperuser
    
##### 4) Очистка базы данных при необходимости

     docker-compose down -v

**Запуск без использования docker:**

#### 1) Создание окружения

    pip install virtualenv
    python3 -m venv venv
    venv/bin/activate

##### 2) Установка нужных пакетов

    pip install -r requirements.txt
    
##### 3) Миграции и сбор статических файлов

    python manage.py makemigrations
    python manage.py migrate
    python manage.py collectstatic

##### 4) Создание супер пользователя для доступа к Django Admin Panel

     python manage.py createsuperuser
    
##### 5) Запуск приложения
    
    python manage.py runserver