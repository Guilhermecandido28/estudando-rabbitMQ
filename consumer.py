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


        # Montagem do texto do recibo
        texto_recibo = 'LOJA JK MODAS E VARIEDADES\n'
        texto_recibo += f'{data}\n\n'
        texto_recibo += f"============= Recibo de Compra =============\n\n"
        texto_recibo += f"Vendedor: {vendedor}\n"
        texto_recibo += f"Forma de Pagamento: {forma_pagamento}\n"
        texto_recibo += "---------------------------------\n"
        texto_recibo += "Produtos\t\t\t\tPreço\t\t\t\tQtd\n"
        texto_recibo += "---------------------------------\n"

        # Quebrar os campos concatenados do dicionário recibo para exibir separadamente
        descricao_list = recibo['descricao'].split(', ')
        venda_list = recibo['venda'].split(', ')
        quantidade_list = recibo['quantidade'].split(', ')

        # Iterar sobre os produtos para adicioná-los ao recibo
        for i in range(len(descricao_list)):
            texto_recibo += f"{descricao_list[i]}\t\t\t{venda_list[i]}\t\t\t{quantidade_list[i]}\n"

        texto_recibo += "---------------------------------\n"
        texto_recibo += f"Total: R${str(total).replace('.',',')}\n"
        texto_recibo += "----------------------------------\n"
        texto_recibo += "Trocas somente serão realizadas mediante a apresentação deste cupom e em 10 dias corridos.\n\n\n"
        texto_recibo += 'Nos siga no Instagram:\n'
        texto_recibo += '@jk_modas_e_variedades\n\n\n'
        texto_recibo += 'Nos chame no Whatsapp:\n'
        texto_recibo += "(11)93482-2157\n\n\n"
        texto_recibo += 'VOLTE SEMPRE!'


        print(texto_recibo)
        try:
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                job = win32print.StartDocPrinter(hPrinter, 1, ("Print Job", None, "RAW"))
                win32print.StartPagePrinter(hPrinter)



                # Converte o texto para cp850
                encoded_text = texto_recibo.encode('cp850')
                print(f"Texto codificado para cp850: {encoded_text}")  # Imprime a representação codificada para depuração

                # Envia o texto para a impressora
                win32print.WritePrinter(hPrinter, encoded_text)

                #corta o papel
                cut_command = b'\x1d\x56\x00'
                win32print.WritePrinter(hPrinter, cut_command)

                win32print.EndPagePrinter(hPrinter)
                win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            print("Arquivo de texto impresso com sucesso.")
        except Exception as e:
            print(f"Erro ao imprimir: {e}")



rabit_consumer = RabbitMQConsumer(minha_callback)
rabit_consumer.start()