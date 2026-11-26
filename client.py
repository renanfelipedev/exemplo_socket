import socket
import threading
from datetime import datetime

# Cores ANSI para o terminal
AZUL = "\033[94m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CINZA = "\033[90m"
RESET = "\033[0m"

endereco = '127.0.0.1'
porta = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"{CINZA}==============================================={RESET}")
meu_nome = input(f"{AMARELO}Informe seu nome no chat: {RESET}").strip() or "Cliente"

client.connect((endereco, porta))
client.sendall(meu_nome.encode('utf-8'))

print(f"{VERDE}✓ Conectado ao servidor!{RESET}")
print(f"{CINZA}Dica: digite suas mensagens e pressione Enter para enviar.{RESET}")
print(f"{CINZA}==============================================={RESET}\n")

def receber_mensagens():
    """Thread que fica escutando as mensagens que chegam da rede."""
    while True:
        try:
            mensagem = client.recv(1024).decode('utf-8')
            if not mensagem:
                print(f"\n{VERMELHO}● [Conexão com o servidor foi encerrada]{RESET}")
                break
            print(f"{mensagem}")
        except:
            break

threading.Thread(target=receber_mensagens, daemon=True).start()

try:
    while True:
        mensagem = input().strip()
        if mensagem:
            hora = datetime.now().strftime("%H:%M")
            print(f"{CINZA}[{hora}]{RESET} {VERDE}Você:{RESET} {mensagem}")
            client.sendall(mensagem.encode('utf-8'))
except KeyboardInterrupt:
    print(f"\n\n{VERMELHO}● [Você saiu do chat]{RESET}")
finally:
    client.close()
