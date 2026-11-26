import socket
import threading

# 1. Configurações básicas de rede
endereco = '0.0.0.0'
porta = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((endereco, porta))
server.listen()

# Lista para guardar os sockets de todos os clientes conectados
clientes = []

# Nome do servidor para identificação no chat
nome_servidor = input("Informe o nome do servidor: ")

def transmitir(mensagem, remetente=None):
    """Envia uma mensagem para todos os clientes conectados."""
    for cliente in clientes:
        if cliente != remetente:
            try:
                cliente.sendall(mensagem.encode('utf-8'))
            except:
                clientes.remove(cliente)

def atender_cliente(conexao):
    """Função executada por uma Thread exclusiva para cada cliente."""
    # A primeira mensagem recebida é o nome do cliente
    nome_cliente = conexao.recv(1024).decode('utf-8')
    clientes.append(conexao)

    print(f"[{nome_cliente}] entrou no chat.")
    transmitir(f"[{nome_cliente}] entrou no chat.", remetente=conexao)

    while True:
        try:
            mensagem = conexao.recv(1024).decode('utf-8')
            if not mensagem:
                break
            
            # Exibe no servidor e repassa aos outros clientes
            msg_formatada = f"{nome_cliente}: {mensagem}"
            print(msg_formatada)
            transmitir(msg_formatada, remetente=conexao)
        except:
            break

    # Quando o cliente sai ou perde conexão
    clientes.remove(conexao)
    conexao.close()
    print(f"[{nome_cliente}] saiu do chat.")
    transmitir(f"[{nome_cliente}] saiu do chat.")

def enviar_servidor():
    """Permite ao próprio servidor também digitar mensagens no chat."""
    while True:
        texto = input()
        if texto:
            msg = f"{nome_servidor}: {texto}"
            transmitir(msg)

# Inicia uma thread para o servidor poder digitar sem travar o accept()
threading.Thread(target=enviar_servidor, daemon=True).start()

print(f"Servidor aguardando conexões na porta {porta}...")

# Loop principal: apenas aguarda novas conexões
try:
    while True:
        conexao, endereco_cliente = server.accept()
        # Cria um atendente (Thread) para o novo cliente
        threading.Thread(target=atender_cliente, args=(conexao,), daemon=True).start()
except KeyboardInterrupt:
    print("\nServidor finalizado.")
finally:
    server.close()
