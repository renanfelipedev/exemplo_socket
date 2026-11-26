import socket
from datetime import datetime

# Cores ANSI para destacar as mensagens no terminal
AZUL = "\033[94m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CINZA = "\033[90m"
RESET = "\033[0m"

# 1. Cria e conecta o socket do cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

endereco_servidor = ('127.0.0.1', 5555)
print(f"{CINZA}Conectando ao servidor em {endereco_servidor[0]}:{endereco_servidor[1]}...{RESET}")
client.connect(endereco_servidor)

print(f"{CINZA}==============================================={RESET}")
print(f"{VERDE}   CONECTADO COM SUCESSO AO SERVIDOR!{RESET}")
print(f"{CINZA}   Dica: digite '{VERMELHO}sair{CINZA}' para encerrar a conversa.{RESET}")
print(f"{CINZA}==============================================={RESET}\n")

try:
    while True:
        # 1. Cliente digita a mensagem
        mensagem = input().strip()
        if not mensagem:
            continue

        hora = datetime.now().strftime("%H:%M")
        print(f"{CINZA}[{hora}]{RESET} {VERDE}Você:{RESET} {mensagem}")
        client.sendall(mensagem.encode('utf-8'))

        # Verifica se o cliente quer encerrar
        if mensagem.lower() == 'sair':
            print(f"\n{VERMELHO}● [Você encerrou a conversa]{RESET}")
            break

        # 2. Aguarda a resposta do servidor
        resposta = client.recv(1024).decode('utf-8')
        hora_resposta = datetime.now().strftime("%H:%M")

        # Verifica se o servidor encerrou
        if not resposta or resposta.lower() == 'sair':
            print(f"\n{VERMELHO}● [Servidor encerrou a conversa]{RESET}")
            break

        print(f"{CINZA}[{hora_resposta}]{RESET} {AMARELO}Servidor:{RESET} {resposta}")

except KeyboardInterrupt:
    print(f"\n\n{VERMELHO}● [Encerrado pelo usuário]{RESET}")
finally:
    client.close()
    print(f"\n{CINZA}Conexão fechada com sucesso.{RESET}")
