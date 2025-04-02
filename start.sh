#!/bin/bash

# 等待MySQL就绪
# echo "Waiting for MySQL..."
# while ! nc -z db 3306; do
#   sleep 1
# done

# # 额外等待几秒确保MySQL完全就绪
# sleep 5

# echo "MySQL started"

# 应用数据库迁移
python manage.py migrate

# 启动服务器
python manage.py runserver 0.0.0.0:8000