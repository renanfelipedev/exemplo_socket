import socket

# 1. Cria e conecta o socket do cliente
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

endereco_servidor = ('127.0.0.1', 5555)
client.connect(endereco_servidor)

print("Conectado ao servidor!")
print("Chat iniciado! Digite 'sair' para encerrar a qualquer momento.\n")

try:
    while True:
        mensagem = input("Cliente: ").strip()
        client.sendall(mensagem.encode('utf-8'))

        if mensagem.lower() == 'sair':
            print("\n[Você encerrou a conversa]")
            break

        resposta = client.recv(1024).decode('utf-8')

        if not resposta or resposta.lower() == 'sair':
            print("\n[Servidor encerrou a conversa]")
            break

        print(f"Servidor: {resposta}")

except KeyboardInterrupt:
    print("\n\nEncerrado pelo usuário.")
finally:
    client.close()
    print("Conexão fechada.")
