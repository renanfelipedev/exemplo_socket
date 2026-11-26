import socket
from datetime import datetime

# Cores ANSI para destacar as mensagens no terminal
AZUL = "\033[94m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CINZA = "\033[90m"
RESET = "\033[0m"

# 1. Cria e configura o socket do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

endereco = ('0.0.0.0', 5555)
server.bind(endereco)
server.listen(1)

print(f"{CINZA}==============================================={RESET}")
print(f"{AMARELO}   SERVIDOR DE CHAT INICIADO NA PORTA {endereco[1]}{RESET}")
print(f"{CINZA}   Aguardando cliente conectar...{RESET}")
print(f"{CINZA}==============================================={RESET}\n")

conexao, endereco_cliente = server.accept()
print(f"{VERDE}✓ Cliente conectado:{RESET} {endereco_cliente[0]}:{endereco_cliente[1]}")
print(f"{CINZA}Dica: digite '{VERMELHO}sair{CINZA}' para encerrar a conversa.{RESET}")
print(f"{CINZA}-----------------------------------------------{RESET}\n")

try:
    while True:
        # 1. Recebe a mensagem do cliente
        mensagem = conexao.recv(1024).decode('utf-8')
        hora = datetime.now().strftime("%H:%M")

        # Verifica se o cliente quer encerrar
        if not mensagem or mensagem.lower() == 'sair':
            print(f"\n{VERMELHO}● [Cliente encerrou a conversa]{RESET}")
            break

        print(f"{CINZA}[{hora}]{RESET} {AZUL}Cliente:{RESET} {mensagem}")

        # 2. Servidor digita a resposta
        resposta = input().strip()
        if not resposta:
            continue

        hora = datetime.now().strftime("%H:%M")
        print(f"{CINZA}[{hora}]{RESET} {VERDE}Você:{RESET} {resposta}")
        conexao.sendall(resposta.encode('utf-8'))

        # Verifica se o servidor quer encerrar
        if resposta.lower() == 'sair':
            print(f"\n{VERMELHO}● [Você encerrou a conversa]{RESET}")
            break

except KeyboardInterrupt:
    print(f"\n\n{VERMELHO}● [Encerrado pelo usuário]{RESET}")
finally:
    conexao.close()
    server.close()
    print(f"\n{CINZA}Conexão fechada com sucesso.{RESET}")
