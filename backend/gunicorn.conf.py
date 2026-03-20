# Gunicorn Production Configuration
workers = 2
worker_class = "gthread"
threads = 2
worker_connections = 100
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
loglevel = "info"
accesslog = "-"
errorlog = "-"