FROM python:3.11.7-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 创建必要的目录
RUN mkdir -p /data/apps/web/logs/zhongyue-django \
    && mkdir -p /data/apps/web/static \
    && mkdir -p /data/apps/web/media \
    && touch /data/apps/web/logs/zhongyue-django/access.log \
    && touch /data/apps/web/logs/zhongyue-django/error.log \
    && chmod -R 777 /data/apps/web/logs/zhongyue-django \
    && chmod -R 777 /data/apps/web/static \
    && chmod -R 777 /data/apps/web/media

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件
COPY . .

# 设置权限
RUN chmod +x /app/start.sh