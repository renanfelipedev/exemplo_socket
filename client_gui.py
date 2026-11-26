import re
import socket
import threading
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, messagebox

# Remove códigos de cores ANSI caso venham do servidor em terminal
ANSI_REGEX = re.compile(r'\x1b\[[0-9;]*m')

client_socket = None
conectado = False

def adicionar_mensagem(texto, tag=None):
    """Insere uma mensagem na área de chat de forma segura na UI."""
    area_chat.config(state=tk.NORMAL)
    area_chat.insert(tk.END, texto + "\n", tag)
    area_chat.config(state=tk.DISABLED)
    area_chat.see(tk.END)

def receber_mensagens():
    """Thread para receber mensagens do servidor sem travar a janela."""
    global conectado
    while conectado:
        try:
            dados = client_socket.recv(1024).decode('utf-8')
            if not dados:
                break
            texto_limpo = ANSI_REGEX.sub('', dados).strip()
            if texto_limpo:
                janela.after(0, adicionar_mensagem, texto_limpo, "outros")
        except:
            break

    if conectado:
        conectado = False
        janela.after(0, ao_desconectar)

def ao_desconectar():
    """Atualiza os botões quando a conexão é encerrada."""
    adicionar_mensagem("● Desconectado do servidor.", "sistema")
    btn_conectar.config(text="Conectar", bg="#2e7d32")
    entrada_ip.config(state=tk.NORMAL)
    entrada_porta.config(state=tk.NORMAL)
    entrada_nome.config(state=tk.NORMAL)
    entrada_msg.config(state=tk.DISABLED)
    btn_enviar.config(state=tk.DISABLED)

def conectar_ou_desconectar():
    """Conecta ao servidor ou encerra a conexão atual."""
    global client_socket, conectado

    if conectado:
        conectado = False
        try:
            client_socket.close()
        except:
            pass
        ao_desconectar()
        return

    ip = entrada_ip.get().strip()
    porta_str = entrada_porta.get().strip()
    nome = entrada_nome.get().strip() or "Cliente"

    if not ip or not porta_str.isdigit():
        messagebox.showwarning("Atenção", "Informe um IP e uma porta válidos.")
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, int(porta_str)))
        client_socket.sendall(nome.encode('utf-8'))
        conectado = True

        adicionar_mensagem(f"✓ Conectado em {ip}:{porta_str} como '{nome}'", "sistema")
        btn_conectar.config(text="Desconectar", bg="#c62828")
        entrada_ip.config(state=tk.DISABLED)
        entrada_porta.config(state=tk.DISABLED)
        entrada_nome.config(state=tk.DISABLED)
        entrada_msg.config(state=tk.NORMAL)
        btn_enviar.config(state=tk.NORMAL)
        entrada_msg.focus()

        threading.Thread(target=receber_mensagens, daemon=True).start()
    except Exception as ex:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar:\n{ex}")

def enviar_mensagem(event=None):
    """Envia a mensagem digitada para o servidor."""
    if not conectado:
        return

    texto = entrada_msg.get().strip()
    if not texto:
        return

    try:
        client_socket.sendall(texto.encode('utf-8'))
        hora = datetime.now().strftime("%H:%M")
        adicionar_mensagem(f"[{hora}] Você: {texto}", "voce")
        entrada_msg.delete(0, tk.END)
    except Exception as ex:
        messagebox.showerror("Erro", f"Falha ao enviar mensagem:\n{ex}")

# --- Construção da Interface Gráfica (Tkinter) ---
janela = tk.Tk()
janela.title("Chat Socket - Cliente")
janela.geometry("560x500")
janela.configure(bg="#1e1e2e")

# Frame superior (Conexão)
frame_topo = tk.Frame(janela, bg="#2b2b3d", pady=10, padx=10)
frame_topo.pack(fill=tk.X)

tk.Label(frame_topo, text="IP:", bg="#2b2b3d", fg="white").grid(row=0, column=0, padx=4)
entrada_ip = tk.Entry(frame_topo, width=14)
entrada_ip.insert(0, "127.0.0.1")
entrada_ip.grid(row=0, column=1, padx=4)

tk.Label(frame_topo, text="Porta:", bg="#2b2b3d", fg="white").grid(row=0, column=2, padx=4)
entrada_porta = tk.Entry(frame_topo, width=6)
entrada_porta.insert(0, "5555")
entrada_porta.grid(row=0, column=3, padx=4)

tk.Label(frame_topo, text="Nome:", bg="#2b2b3d", fg="white").grid(row=0, column=4, padx=4)
entrada_nome = tk.Entry(frame_topo, width=12)
entrada_nome.insert(0, "Aluno")
entrada_nome.grid(row=0, column=5, padx=4)

btn_conectar = tk.Button(
    frame_topo, text="Conectar", bg="#2e7d32", fg="white",
    command=conectar_ou_desconectar, padx=10
)
btn_conectar.grid(row=0, column=6, padx=6)

# Área central de mensagens
area_chat = scrolledtext.ScrolledText(
    janela, state=tk.DISABLED, wrap=tk.WORD,
    bg="#181825", fg="#cdd6f4", font=("Menlo", 11), padx=10, pady=10
)
area_chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Estilos de cores para as mensagens
area_chat.tag_config("voce", foreground="#a6e3a1")
area_chat.tag_config("outros", foreground="#89b4fa")
area_chat.tag_config("sistema", foreground="#f9e2af")

# Frame inferior (Digitação e envio)
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
