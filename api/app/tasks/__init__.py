# from celery import Celery
# # from app.settings import Settings
#
# # celery_app = Celery("tasks", broker=Settings().broker_url)
# celery_app = Celery("tasks", broker="amqp://localhost:5672")
