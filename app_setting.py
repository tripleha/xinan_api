bind = "unix:/tmp/uvicorn.sock"

workers = 4
daemon = True
pidfile = "main-app.pid"
accesslog = "main-access.log"
loglevel = "debug"
capture_output = True
errorlog = "main-log.log"
