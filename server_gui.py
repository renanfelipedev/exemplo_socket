import re
import socket
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, messagebox

# Configurações Anti-Spam
LIMITE_MSGS = 5       # Máximo de mensagens permitidas
JANELA_SEGUNDOS = 5   # Intervalo de tempo (em segundos)
TEMPO_TIMEOUT = 10    # Duração do silenciamento (em segundos)

ANSI_REGEX = re.compile(r'\x1b\[[0-9;]*m')

server_socket = None
rodando = False
clientes = []

def adicionar_mensagem(texto, tag=None):
    """Insere uma mensagem na área de chat de forma segura na UI."""
    area_chat.config(state=tk.NORMAL)
    area_chat.insert(tk.END, texto + "\n", tag)
    area_chat.config(state=tk.DISABLED)
    area_chat.see(tk.END)

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
    """Thread para receber mensagens de um cliente conectado."""
    nome_cliente = "Anônimo"
    try:
        nome_cliente = conexao.recv(1024).decode('utf-8').strip() or "Anônimo"
        clientes.append(conexao)

        hora = datetime.now().strftime("%H:%M")
        aviso_entrou = f"[{hora}] ● [{nome_cliente}] entrou no chat."
        janela.after(0, adicionar_mensagem, aviso_entrou, "sistema")
        transmitir(aviso_entrou, remetente=conexao)

        ultimas_msgs = []
        silenciado_ate = 0

        while rodando:
            mensagem = conexao.recv(1024).decode('utf-8')
            if not mensagem:
                break

            agora = time.time()

            # Verifica se o cliente está em timeout
            if agora < silenciado_ate:
                restante = int(silenciado_ate - agora) + 1
                conexao.sendall(f"⚠ Você está em timeout por spam! Aguarde {restante}s.".encode('utf-8'))
                continue

            # Registra o horário da mensagem e filtra a janela de tempo
            ultimas_msgs.append(agora)
            ultimas_msgs = [t for t in ultimas_msgs if agora - t <= JANELA_SEGUNDOS]

            # Se ultrapassar o limite, aplica o timeout
            if len(ultimas_msgs) > LIMITE_MSGS:
                silenciado_ate = agora + TEMPO_TIMEOUT
                ultimas_msgs.clear()
                hora = datetime.now().strftime("%H:%M")
                aviso_spam = f"[{hora}] ⚠ [{nome_cliente}] recebeu timeout de {TEMPO_TIMEOUT}s por spam!"
                janela.after(0, adicionar_mensagem, aviso_spam, "sistema")
                transmitir(aviso_spam)
                continue

            texto_limpo = ANSI_REGEX.sub('', mensagem).strip()
            hora = datetime.now().strftime("%H:%M")
            msg_formatada = f"[{hora}] {nome_cliente}: {texto_limpo}"
            janela.after(0, adicionar_mensagem, msg_formatada, "outros")
            transmitir(msg_formatada, remetente=conexao)
    except:
        pass
    finally:
        if conexao in clientes:
            clientes.remove(conexao)
        try:
            conexao.close()
        except:
            pass
        if rodando:
            hora = datetime.now().strftime("%H:%M")
            aviso_saiu = f"[{hora}] ● [{nome_cliente}] saiu do chat."
            janela.after(0, adicionar_mensagem, aviso_saiu, "sistema")
            transmitir(aviso_saiu)

def aceitar_conexoes():
    """Loop em thread que aceita novos clientes."""
    while rodando:
        try:
            conexao, _ = server_socket.accept()
            threading.Thread(target=atender_cliente, args=(conexao,), daemon=True).start()
        except:
            break

def iniciar_ou_parar():
    """Inicia ou encerra o servidor."""
    global server_socket, rodando

    if rodando:
        rodando = False
        for c in list(clientes):
            try:
                c.close()
            except:
                pass
        clientes.clear()
        try:
            server_socket.close()
        except:
            pass
        adicionar_mensagem("● Servidor encerrado.", "sistema")
        btn_iniciar.config(text="Iniciar Servidor", bg="#2e7d32")
        entrada_porta.config(state=tk.NORMAL)
        entrada_nome.config(state=tk.NORMAL)
        entrada_msg.config(state=tk.DISABLED)
        btn_enviar.config(state=tk.DISABLED)
        return

    porta_str = entrada_porta.get().strip()
    if not porta_str.isdigit():
        messagebox.showwarning("Atenção", "Informe uma porta válida.")
        return

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', int(porta_str)))
        server_socket.listen()
        rodando = True

        adicionar_mensagem(f"✓ Servidor iniciado na porta {porta_str}. Aguardando conexões...", "sistema")
        btn_iniciar.config(text="Parar Servidor", bg="#c62828")
        entrada_porta.config(state=tk.DISABLED)
        entrada_nome.config(state=tk.DISABLED)
        entrada_msg.config(state=tk.NORMAL)
        btn_enviar.config(state=tk.NORMAL)
        entrada_msg.focus()

        threading.Thread(target=aceitar_conexoes, daemon=True).start()
    except Exception as ex:
        messagebox.showerror("Erro", f"Não foi possível iniciar o servidor:\n{ex}")

def enviar_mensagem(event=None):
    """Envia mensagem do servidor para todos os clientes."""
    if not rodando:
        return

    texto = entrada_msg.get().strip()
    if not texto:
        return

    nome_servidor = entrada_nome.get().strip() or "Servidor"
    hora = datetime.now().strftime("%H:%M")

    adicionar_mensagem(f"[{hora}] Você ({nome_servidor}): {texto}", "voce")
    transmitir(f"[{hora}] {nome_servidor}: {texto}")
    entrada_msg.delete(0, tk.END)

# --- Construção da Interface Gráfica (Tkinter) ---
janela = tk.Tk()
janela.title("Chat Socket - Servidor")
janela.geometry("560x500")
janela.configure(bg="#1e1e2e")

frame_topo = tk.Frame(janela, bg="#2b2b3d", pady=10, padx=10)
frame_topo.pack(fill=tk.X)

tk.Label(frame_topo, text="Porta:", bg="#2b2b3d", fg="white").grid(row=0, column=0, padx=4)
entrada_porta = tk.Entry(frame_topo, width=8)
entrada_porta.insert(0, "5555")
entrada_porta.grid(row=0, column=1, padx=4)

tk.Label(frame_topo, text="Nome:", bg="#2b2b3d", fg="white").grid(row=0, column=2, padx=4)
entrada_nome = tk.Entry(frame_topo, width=15)
entrada_nome.insert(0, "Servidor")
entrada_nome.grid(row=0, column=3, padx=4)

btn_iniciar = tk.Button(
    frame_topo, text="Iniciar Servidor", bg="#2e7d32", fg="white",
    command=iniciar_ou_parar, padx=10
)
btn_iniciar.grid(row=0, column=4, padx=8)

area_chat = scrolledtext.ScrolledText(
    janela, state=tk.DISABLED, wrap=tk.WORD,
    bg="#181825", fg="#cdd6f4", font=("Menlo", 11), padx=10, pady=10
)
area_chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

area_chat.tag_config("voce", foreground="#a6e3a1")
area_chat.tag_config("outros", foreground="#89b4fa")
area_chat.tag_config("sistema", foreground="#f9e2af")

frame_baixo = tk.Frame(janela, bg="#1e1e2e", pady=8, padx=10)
frame_baixo.pack(fill=tk.X)

entrada_msg = tk.Entry(frame_baixo, font=("Menlo", 11), state=tk.DISABLED)
entrada_msg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
entrada_msg.bind("<Return>", enviar_mensagem)

btn_enviar = tk.Button(
    frame_baixo, text="Enviar", bg="#1976d2", fg="white",
    command=enviar_mensagem, state=tk.DISABLED, padx=15
)
btn_enviar.pack(side=tk.RIGHT)

janela.mainloop()
