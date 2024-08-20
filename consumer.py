import pika
import win32print
import json


class RabbitMQConsumer:
    def __init__(self, callback) -> None:
        self.__host = '34.151.232.173'
        self.__port = 5672
        self.__username = 'guest'
        self.__password = 'guest'
        self.__queue = 'data_queue'
        self.__callback = callback
        self.__channel = self.__create_channel()

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(
                username= self.__username,
                password= self.__password
            ),
        )

        channel = pika.BlockingConnection(connection_parameters).channel()
        channel.queue_declare(
            queue=self.__queue,
            durable=True,    
        )

        channel.basic_consume(
            queue=self.__queue,
            auto_ack=True,
            on_message_callback=self.__callback
        )
        return channel
    
    def start(self):
        print(f'Listen RabbitMQ on Port 5672')
        self.__channel.start_consuming()

def minha_callback(ch, method, properties, body, printer_name='cupom'):
        mensagem_str = body.decode('latin1')
    
    # Carregar a mensagem JSON
        mensagem_json = json.loads(mensagem_str)
        
        # Acessar e processar os dados
        data = mensagem_json['data']
        vendedor = mensagem_json['vendedor']
        cliente = mensagem_json['cliente']
        forma_pagamento = mensagem_json['forma_pagamento']
        total = mensagem_json['total']
        recibo = mensagem_json['recibo']
        
        # Aqui você pode fazer o que precisar com os dados
        text = f"Data: {data}\n"
        text += f"Vendedor: {vendedor}\n"
        text += f"Cliente: {cliente}\n"
        text += f"Forma de Pagamento: {forma_pagamento}\n"
        text += f"Total: {total}\n"
        text += f"Recibo: {recibo}\n"

        try:
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                job = win32print.StartDocPrinter(hPrinter, 1, ("Print Job", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)



                # Converte o texto para cp850
                encoded_text = text.encode('cp850')
                print(f"Texto codificado para cp850: {encoded_text}")  # Imprime a representação codificada para depuração

                # Envia o texto para a impressora
                win32print.WritePrinter(hPrinter, encoded_text)

                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            print("Arquivo de texto impresso com sucesso.")
        except Exception as e:
            print(f"Erro ao imprimir: {e}")



rabit_consumer = RabbitMQConsumer(minha_callback)
rabit_consumer.start()