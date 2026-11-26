# 💬 Exemplo Prático de Sockets em Python: Chat Multicliente

Bem-vindo ao projeto didático de comunicação em rede! Este projeto foi desenvolvido para introduzir os conceitos fundamentais de **Sockets**, **Arquitetura Cliente-Servidor** e **Concorrência com Threads** de forma prática e visual.

---

## 🎯 O que é este projeto?

É uma aplicação de **Chat em Tempo Real** composta por dois programas:
* **`server.py` (Servidor):** A "central" que gerencia as conexões, recebe mensagens e as distribui para todos os participantes (incluindo ele próprio).
* **`client.py` (Cliente):** O programa que cada participante executa no seu computador/terminal para entrar na sala e conversar.

---

## 🧠 Conceitos Fundamentais (Para entender antes do código)

### 1. O que é um Socket?
Imagine um **Socket** como uma tomada ou um **telefone**:
* Para duas pessoas conversarem à distância, cada uma precisa ter um aparelho telefônico na mão (**Socket**).
* Para ligar para alguém, você precisa de um endereço (**Endereço IP**) e de um ramal específico (**Porta lógica**).
* O cabo invisível que conecta os dois telefones usando o protocolo TCP garante que nenhuma palavra dita seja perdida ou chegue fora de ordem.

---

### 2. O Ciclo de Vida dos Comandos

| Comando | O que significa na vida real? | Onde é usado? |
| :--- | :--- | :--- |
| `socket.socket(...)` | Comprar o aparelho de telefone | Servidor e Cliente |
| `bind((ip, porta))` | Registrar o seu número de telefone e ramal | Servidor |
| `listen()` | Ativar a campainha e esperar chamadas | Servidor |
| `connect((ip, porta))` | Discar para o número do servidor | Cliente |
| `accept()` | Atender a chamada e começar uma conversa exclusiva | Servidor |
| `sendall(...)` | Falar no fone (precisa codificar em bytes: `.encode()`) | Ambos |
| `recv(...)` | Ouvir o que foi dito (precisa decodificar bytes: `.decode()`) | Ambos |
| `close()` | Desligar o telefone | Ambos |

---

### 3. Por que usamos Threads? (A Analogia do Restaurante)

Se você tentar fazer tudo em uma linha única de código, seu programa trava na primeira ação que fica "esperando":
* `accept()` trava o programa esperando alguém conectar.
* `recv()` trava o programa esperando alguém enviar uma mensagem.
* `input()` trava o programa esperando você digitar algo.

Para resolver isso, usamos **Threads**:
> Pense no **Servidor** como um restaurante:
> * O loop principal do servidor é o **recepcionista** na porta. Ele só faz uma coisa: esperar clientes com `server.accept()`.
> * Quando um cliente chega, o recepcionista não para o restaurante para atendê-lo. Ele chama um **garçom exclusivo (`Thread`)** para cuidar daquela mesa (`atender_cliente`).
> * Assim, se 10 clientes entrarem, teremos 10 garçons trabalhando ao mesmo tempo, e novos clientes ainda poderão entrar livremente!

No **Cliente**, usamos o mesmo raciocínio:
* **Ouvido (Thread em segundo plano):** Fica só escutando o `client.recv()` para mostrar mensagens na tela imediatamente.
* **Boca (Loop principal):** Fica livre esperando você digitar no `input()` e enviar com `sendall()`.

---

## 🚀 Como Executar o Projeto

Você precisará de pelo menos **dois terminais** abertos no mesmo computador (ou computadores na mesma rede).

### Passo 1: Iniciar o Servidor
Abra o primeiro terminal e execute:
```bash
python3 server.py
```
1. Digite o nome que representará o servidor no chat (ex: `Admin`).
2. O servidor exibirá: `Servidor aguardando conexões na porta 5555...`.

---

### Passo 2: Iniciar o Primeiro Cliente
Abra um segundo terminal e execute:
```bash
python3 client.py
```
1. Digite seu nome (ex: `Alice`).
2. Uma mensagem de boas-vindas aparecerá no servidor e no cliente!

---

### Passo 3: Iniciar Mais Clientes
Abra um terceiro terminal e execute o cliente novamente:
```bash
python3 client.py
```
1. Digite outro nome (ex: `Bob`).
2. Agora todos (Alice, Bob e o Servidor) podem trocar mensagens em tempo real!

---

## 🔍 Destaques do Código para a Aula

### No `server.py`:
```python
# 1. Cria a tomada de rede TCP/IP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Associa a máquina ao IP e à Porta
server.bind(('0.0.0.0', 5555))

# 3. Coloca o servidor em modo de escuta
server.listen()

# 4. Atende um cliente e passa o atendimento para uma Thread dedicada
conexao, endereco = server.accept()
threading.Thread(target=atender_cliente, args=(conexao,)).start()
```

### No `client.py`:
```python
# 1. Conecta ao endereço e porta do servidor
client.connect(('127.0.0.1', 5555))

# 2. Dispara a Thread de escuta contínua
threading.Thread(target=receber_mensagens, daemon=True).start()

# 3. Permite digitação contínua
while True:
    msg = input()
    client.sendall(msg.encode('utf-8'))
```

---

## 💡 Desafios e Atividades Sugeridas para os Alunos

1. **Alterar a porta:** Mudar a porta `5555` para outra porta (ex: `8080`) e verificar o que acontece se o cliente tentar conectar na porta errada.
2. **Chat entre máquinas diferentes:** Rodar o `server.py` em um computador, descobrir o IP local dele (`ipconfig` ou `ifconfig`) e conectar outro computador alterando a variável `endereco` no `client.py`.
3. **Comando de saída:** Adicionar uma regra no cliente para que, se ele digitar `/sair`, o programa desconecte sozinho.
