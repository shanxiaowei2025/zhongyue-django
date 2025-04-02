# 指定基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /app

# 安装系统依赖
# 更新包列表并安装系统依赖
RUN apt-get update && apt-get install -y \  
    # 安装MySQL客户端
    default-libmysqlclient-dev \ 
    # 安装构建工具
    build-essential \ 
    # 安装netcat
    netcat-openbsd \ 
    # 安装pkg-config
    pkg-config \ 
    # 安装MySQL客户端
    default-mysql-client \ 
    # 删除包列表
    && rm -rf /var/lib/apt/lists/* 

# 修改目录创建
# 创建静态文件目录
RUN mkdir -p /app/storage/static \ 
    # 创建媒体文件目录
    && mkdir -p /app/storage/media \ 
    # 创建日志目录
    && mkdir -p /data/apps/web/logs/zhongyue-django \ 
    # 创建访问日志
    && touch /data/apps/web/logs/zhongyue-django/access.log \ 
    # 创建错误日志
    && touch /data/apps/web/logs/zhongyue-django/error.log \ 
    # 设置权限
    && chmod -R 777 /app/storage \ 
    # 设置权限
    && chmod -R 777 /data/apps/web/logs/zhongyue-django 

# 添加Python路径
ENV PYTHONPATH=/app 

# 复制 requirements.txt
COPY requirements.txt .

# 复制其他项目文件
COPY . .

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 设置权限
RUN chmod +x start.sh

# 暴露端口
EXPOSE 8000

# Dockerfile中添加
VOLUME ["/app/storage/static"]

# 启动服务
CMD ["./start.sh"]