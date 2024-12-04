#!/bin/bash

# 等待MySQL启动
echo "Waiting for MySQL..."
while ! nc -z $DB_HOST 3306; do
    sleep 1
done
echo "MySQL started"

# 收集静态文件
python manage.py collectstatic --noinput

# 删除所有迁移文件
echo "Cleaning old migrations..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 首先为 users 应用生成迁移文件
echo "Making migrations for users app..."
python manage.py makemigrations users

# 然后为其他应用生成迁移文件
echo "Making migrations for other apps..."
python manage.py makemigrations

# 先执行 users 应用的迁移
echo "Applying users migrations..."
python manage.py migrate users

# 再执行其他应用的迁移
echo "Applying other migrations..."
python manage.py migrate

# 使用gunicorn启动应用
exec gunicorn -c gunicorn_config.py zhongyue_django.wsgi:application