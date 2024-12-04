import multiprocessing

# 绑定的ip和端口号
bind = "0.0.0.0:10000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = 'sync'

# 最大客户端并发数量
worker_connections = 2000

# 进程名称
proc_name = 'gunicorn_zhongyue'

# 超时时间
timeout = 30

# 访问日志文件
accesslog = '/data/apps/web/logs/zhongyue-django/access.log'

# 错误日志文件
errorlog = '/data/apps/web/logs/zhongyue-django/error.log'

# 日志级别
loglevel = 'info'
