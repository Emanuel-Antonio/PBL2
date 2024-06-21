from flask import Flask, request, jsonify
import threading
import time
import requests

app = Flask(__name__)

# Estado do nó
node_state = {
    "node_id": 1,  # Atualize para o ID do nó específico
    "node_urls": ["http://192.168.1.105:5000", "http://192.168.1.106:5000"],  # Lista de URLs dos nós
    "current_index": 0,  # Índice do nó atual na lista
    "has_token": False,
    "last_token_time": time.time(),
    "token_timeout": 30,  # Tempo máximo que o nó pode ficar sem token (em segundos)
    "token_check_interval": 1,  # Intervalo de checagem (em segundos)
    "token_sequence": 0
}

def pass_token():
    global node_state
    initial_index = node_state["current_index"]
    while True:  
        if node_state["has_token"]:
            next_node_url = (node_state["current_index"] + 1) % len(node_state["node_urls"])
            print(f"Tentando passar o token para: {node_state["node_urls"][next_node_url]}")
            time.sleep(2)      
            try:
                response = requests.post(f"{node_state["node_urls"][next_node_url]}/receive_token",json={"Token sequence": node_state['token_sequence']+1}, timeout=5)
                if response.status_code == 200:
                    print(f"Token passado para o próximo nó: {next_node_url}")
                    node_state["last_token_time"] = time.time()
                    if next_node_url != node_state["node_urls"][initial_index]:
                        node_state["has_token"] = False
                else:
                    print(f"Falha ao passar o token para {next_node_url}: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Erro ao passar o token para {next_node_url}: {e}")
            
            # Tentar o próximo nó na lista
            print((node_state["current_index"] + 1) % len(node_state["node_urls"]))
            #node_state["current_index"] = (node_state["current_index"] + 1) % len(node_state["node_urls"])
            
            # Se voltar ao nó inicial, significa que todos os nós foram tentados
            if node_state["current_index"] == initial_index:
                print("Falha ao passar o token para todos os nós. Reiniciando tentativa.")

        else:
            time.sleep(1)
            print("Não é possível passar o token: O nó não possui o token.")

def receive_token():
    global node_state
    print("recebi")
    node_state["has_token"] = True
    node_state["last_token_time"] = time.time()
    print(f"Token recebido pelo nó {node_state['node_id']}")
    print(f"Token recebido com sequencia {node_state['token_sequence']}")


def check_token():
    while True:
        time.sleep(node_state["token_check_interval"])
        if not node_state["has_token"] and (time.time() - node_state["last_token_time"] > node_state["token_timeout"]):
            print(f"O nó {node_state['node_id']} está sem o token por muito tempo. Gerando um novo token.")
            receive_token()  # Para fins deste exemplo, simplesmente regeneramos o token

# Rota para receber o token
@app.route('/receive_token', methods=['POST'])
def receive_token_route():
    global node_state
    token_sequence = request.get_json()
    if token_sequence["Token sequence"] > node_state["token_sequence"]:
        node_state["token_sequence"] = token_sequence['Token sequence']
        receive_token()
    return jsonify({"message": "Token recebido"}), 200

# Função para iniciar o servidor Flask
def iniciar_servidor_flask():
    app.run(host='0.0.0.0', port=5000)

def main():
    
    # Inicia o servidor Flask em uma nova thread
    thread_servidor_flask = threading.Thread(target=iniciar_servidor_flask)
    thread_servidor_flask.start()
    
    # Inicializa o nó com o token (apenas para o primeiro nó na rede)
    if node_state["node_id"] == 1:
        receive_token()
    
    # Inicializa a thread que verifica e gera o token periodicamente
    token_thread_pass = threading.Thread(target=pass_token)
    token_thread_pass.start()
    
    # Inicializa a thread que verifica e gera o token periodicamente
    token_thread = threading.Thread(target=check_token)
    token_thread.start()

if __name__ == '__main__':
    main()