import pika

# Подключение к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Создание очереди (если её нет)
channel.queue_declare(queue='python_queue')

# Отправка сообщения
channel.basic_publish(
    exchange='',
    routing_key='python_queue',
    body='Hello from Python!'
)
print(" [x] Sent 'Hello from Python!'")

# Закрытие соединения
connection.close()
