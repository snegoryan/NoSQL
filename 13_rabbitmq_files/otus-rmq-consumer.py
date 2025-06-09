import pika

# Подключение к RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Создание очереди (если её нет)
channel.queue_declare(queue='python_queue')

# Функция для обработки сообщений
def callback(ch, method, properties, body):
    print(f" [x] Received {body}")

# Подписка на очередь
channel.basic_consume(
    queue='python_queue',
    auto_ack=True,  # автоматическое подтверждение получения
    on_message_callback=callback
)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
