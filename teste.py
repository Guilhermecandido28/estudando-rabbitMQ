import pika

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='34.151.232.173',
        port=5672,
        credentials=pika.PlainCredentials('guest', 'guest')
    ))
    print("Conectado ao RabbitMQ com sucesso!")
    connection.close()
except Exception as e:
    print(f"Erro ao conectar ao RabbitMQ: {e}")
