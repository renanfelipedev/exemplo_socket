import socket
import threading
import time
from datetime import datetime

# Configurações Anti-Spam
LIMITE_MSGS = 5       # Máximo de mensagens permitidas
JANELA_SEGUNDOS = 5   # Intervalo de tempo (em segundos)
TEMPO_TIMEOUT = 10    # Duração do silenciamento (em segundos)

# Cores ANSI para o terminal
AZUL = "\033[94m"
VERDE = "\033[92m"
AMARELO = "\033[93m"
VERMELHO = "\033[91m"
CINZA = "\033[90m"
RESET = "\033[0m"

endereco = '0.0.0.0'
porta = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((endereco, porta))
server.listen()

clientes = []

print(f"{CINZA}==============================================={RESET}")
nome_servidor = input(f"{AMARELO}Informe o nome do servidor no chat: {RESET}").strip() or "Servidor"
print(f"{CINZA}==============================================={RESET}")
print(f"{VERDE}✓ Servidor aguardando conexões na porta {porta}...{RESET}\n")

def transmitir(mensagem, remetente=None):
    """Envia a mensagem para todos os clientes conectados."""
    for cliente in list(clientes):
        if cliente != remetente:
            try:
                cliente.sendall(mensagem.encode('utf-8'))
            except:
                if cliente in clientes:
                    clientes.remove(cliente)

def atender_cliente(conexao):
    """Thread exclusiva para cada cliente conectado."""
    nome_cliente = "Anônimo"
    try:
        nome_cliente = conexao.recv(1024).decode('utf-8').strip() or "Anônimo"
        clientes.append(conexao)

        hora = datetime.now().strftime("%H:%M")
        aviso_entrou = f"{CINZA}[{hora}]{RESET} {VERDE}● [{nome_cliente}] entrou no chat.{RESET}"
        print(aviso_entrou)
        transmitir(aviso_entrou, remetente=conexao)

        ultimas_msgs = []
        silenciado_ate = 0

        while True:
            mensagem = conexao.recv(1024).decode('utf-8')
            if not mensagem:
                break

            agora = time.time()

            # Verifica se o cliente está cumprindo timeout
            if agora < silenciado_ate:
                restante = int(silenciado_ate - agora) + 1
                conexao.sendall(f"{VERMELHO}⚠ Você está em timeout por spam! Aguarde {restante}s.{RESET}".encode('utf-8'))
                continue

            # Registra o horário e mantém apenas mensagens dentro da janela de tempo
            ultimas_msgs.append(agora)
            ultimas_msgs = [t for t in ultimas_msgs if agora - t <= JANELA_SEGUNDOS]

            # Se ultrapassar o limite, aplica timeout
            if len(ultimas_msgs) > LIMITE_MSGS:
                silenciado_ate = agora + TEMPO_TIMEOUT
                ultimas_msgs.clear()
                hora = datetime.now().strftime("%H:%M")
                aviso_spam = f"{CINZA}[{hora}]{RESET} {VERMELHO}⚠ [{nome_cliente}] recebeu timeout de {TEMPO_TIMEOUT}s por spam!{RESET}"
                print(aviso_spam)
                transmitir(aviso_spam)
                continue
            
            hora = datetime.now().strftime("%H:%M")
            msg_formatada = f"{CINZA}[{hora}]{RESET} {AZUL}{nome_cliente}:{RESET} {mensagem}"
            print(msg_formatada)
            transmitir(msg_formatada, remetente=conexao)

    except:
        pass
    finally:
        if conexao in clientes:
            clientes.remove(conexao)
        conexao.close()
        hora = datetime.now().strftime("%H:%M")
        aviso_saiu = f"{CINZA}[{hora}]{RESET} {VERMELHO}● [{nome_cliente}] saiu do chat.{RESET}"
        print(aviso_saiu)
        transmitir(aviso_saiu)

def enviar_servidor():
    """Permite ao operador do servidor digitar mensagens no chat."""
    while True:
        try:
            texto = input().strip()
            if texto:
                hora = datetime.now().strftime("%H:%M")
                # Exibe imediatamente no terminal do próprio servidor
                print(f"{CINZA}[{hora}]{RESET} {VERDE}Você:{RESET} {texto}")
                # Envia aos clientes com o nome do servidor
                msg_formatada = f"{CINZA}[{hora}]{RESET} {AMARELO}{nome_servidor}:{RESET} {texto}"
                transmitir(msg_formatada)
        except (KeyboardInterrupt, EOFError):
            break

threading.Thread(target=enviar_servidor, daemon=True).start()

try:
    while True:
        conexao, endereco_cliente = server.accept()
        threading.Thread(target=atender_cliente, args=(conexao,), daemon=True).start()
except KeyboardInterrupt:
    print(f"\n{VERMELHO}● Servidor finalizado.{RESET}")
finally:
    server.close()
