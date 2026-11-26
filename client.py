import socket
import threading

# 1. Configurações de conexão com o servidor
endereco = '127.0.0.1'
porta = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Informa o nome do usuário antes de conectar
meu_nome = input("Informe seu nome: ")

client.connect((endereco, porta))
# Envia o nome como a primeira mensagem de apresentação
client.sendall(meu_nome.encode('utf-8'))
print(f"Conectado ao servidor! Pode começar a conversar.")

def receber_mensagens():
    """Thread que fica apenas escutando tudo que chega da rede."""
    while True:
        try:
            mensagem = client.recv(1024).decode('utf-8')
            if not mensagem:
                print("\nConexão com o servidor foi encerrada.")
                break
            print(mensagem)
        except:
            break

# Inicia a escuta em segundo plano (em paralelo)
threading.Thread(target=receber_mensagens, daemon=True).start()

# O loop principal fica livre para você digitar mensagens
try:
    while True:
        mensagem = input()
        if mensagem:
            client.sendall(mensagem.encode('utf-8'))
except KeyboardInterrupt:
    print("\nVocê saiu do chat.")
finally:
    client.close()
