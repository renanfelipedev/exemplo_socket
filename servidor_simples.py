import socket

# 1. Cria e configura o socket do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

endereco = ('127.0.0.1', 5555)
server.bind(endereco)
server.listen(1)

print(f"Servidor aguardando conexão em {endereco[0]}:{endereco[1]}...")
conexao, endereco_cliente = server.accept()
print(f"Cliente conectado: {endereco_cliente}")
print("Chat iniciado! Digite 'sair' para encerrar a qualquer momento.\n")

try:
    while True:
        mensagem = conexao.recv(1024).decode('utf-8')

        if not mensagem or mensagem.lower() == 'sair':
            print("\n[Cliente encerrou a conversa]")
            break

        print(f"Cliente: {mensagem}")

        resposta = input("Servidor: ").strip()
        conexao.sendall(resposta.encode('utf-8'))

        if resposta.lower() == 'sair':
            print("\n[Você encerrou a conversa]")
            break

except KeyboardInterrupt:
    print("\n\nEncerrado pelo usuário.")
finally:
    conexao.close()
    server.close()
    print("Conexão fechada.")
