import random
from flask import Flask, request, jsonify
import requests
import json
import os
from threading import Lock
import time
import threading

app = Flask(__name__)

# Configurações
#bank = os.getenv("bank")

bank = "192.168.1.104"

# Lista de usuários
users = []
# Lock para sincronização
lock = Lock()

transfers = []
finalizedTransfers = []
idtransfers = []

# Rota para pegar um id para a transacao
@app.route('/id', methods=['GET'])
def get_id():
    id = random.randint(100000, 999999)
    while id in idtransfers:
        id = random.randint(100000, 999999)
    idtransfers.append(id)
    return jsonify(id), 201

# Rota para verificar o status da transacao
@app.route('/status', methods=['GET'])
def get_status():
    id = request.get_json()
    for item in finalizedTransfers:
        print(finalizedTransfers)
        print(id)
        if item[0] == str(id['id']):
            if item[1] == False:
                return jsonify(False), 401
            else:
                return jsonify(item[1]), 201
    return jsonify(False), 401

########################################################## Token ####################################################

# Estado do nó
node_state = {
    "node_id": 1,  # Atualize para o ID do nó específico
    "node_urls": ["http://192.168.1.104:8088", "http://192.168.1.103:8088"],  # Lista de URLs dos nós --> Mudar no Laboratório
    "current_index": 0,  # Índice do nó atual na lista
    "has_token": False,
    "last_token_time": time.time(),
    "token_timeout": 30,  # Tempo máximo que o nó pode ficar sem token (em segundos)
    "token_check_interval": 1,  # Intervalo de checagem (em segundos)
    "token_sequence": 0,
    "pass": False,
    "exec": False
}

def pass_token():
    global node_state
    initial_index = node_state["current_index"]
    while True:  
        if node_state["has_token"] and node_state["pass"]:
            initial_index +=1
            initial_index = initial_index % len(node_state["node_urls"])
            next_node_url = initial_index
            print(f"Tentando passar o token para: {node_state["node_urls"][next_node_url]}")
            try:
                if node_state["node_urls"][next_node_url] != node_state["node_urls"][node_state["current_index"]]:
                    response = requests.post(f"{node_state["node_urls"][next_node_url]}/receive_token",json={"Token sequence": node_state['token_sequence']+1}, timeout=2)
                    if response.status_code == 200:
                        print(f"Token passado para o próximo nó: {next_node_url}")
                        node_state["last_token_time"] = time.time()
                        node_state["has_token"] = False
                        node_state["pass"] = False
                        initial_index = node_state["current_index"] + 1
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
            time.sleep(2)
            print("Não é possível passar o token: O nó não possui o token.")

def receive_token():
    global node_state, transfers, finalizedTransfers
    print("recebi")
    node_state["has_token"] = True
    node_state["last_token_time"] = time.time()
    print(f"Token recebido pelo nó {node_state['node_id']}")
    print(f"Token recebido com sequencia {node_state['token_sequence']}")
    if node_state["exec"] == True:
        try:
            print(transfers)
            ok = transfer(transfers[0])
            print(ok)
            for i in range(len(finalizedTransfers)):
                if finalizedTransfers[i][1]=='':
                    print(finalizedTransfers[i][1])
                    finalizedTransfers[i][1] = ok
                    break
            del transfers[0]
            print(transfers)  
            print(finalizedTransfers)
        except Exception as e:
            pass
    node_state["pass"] = True

def check_token():
    while True:
        time.sleep(node_state["token_check_interval"])
        if not node_state["has_token"] and ((time.time() - node_state["last_token_time"]) > node_state["token_timeout"]):
            print(f"O nó {node_state['node_id']} está sem o token por muito tempo. Gerando um novo token.")
            node_state["exec"] = False
            node_state["token_sequence"] = node_state['token_sequence'] + len(node_state["node_urls"])
            receive_token()  # Para fins deste exemplo, simplesmente regeneramos o token

# Rota para receber o token
@app.route('/receive_token', methods=['POST'])
def receive_token_route():
    global node_state
    token_sequence = request.get_json()
    if token_sequence["Token sequence"] > node_state["token_sequence"]:
        node_state["token_sequence"] = token_sequence['Token sequence']
        node_state["exec"] = True
        receive_token()
    return jsonify({"message": "Token recebido"}), 200

########################################################## Token ####################################################
    
# Rota para verificar login de todos os usuários do Banco
@app.route('/login', methods=['POST'])
def set_login():
    data = request.get_json()
    user_id = data['id']
    password = data['password']
    print(data)
    for item in users:
        if item['id'] == user_id and item['senha'] == password:
            return jsonify({'message': 'ok'}), 201
    return jsonify({'message': 'falha'}), 401

# Rota para listar todos os usuários do Banco
@app.route('/users', methods=['GET'])
def get_users():
    with lock:
        users_no_password = [user.copy() for user in users]
        for user in users_no_password:
            del user['senha']
        return jsonify(users_no_password), 201

# Rota para obter um usuário por ID no Banco
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with lock:
        users_no_password = [user.copy() for user in users]
        print(users_no_password)
        for user in users_no_password:
            print(user, "a")
            if user['id'] == str(user_id):
                del user['senha']
                return jsonify(user), 201
    return jsonify({'message': 'User não encontrado'}), 401

# Rota para criar um novo usuário no Banco
@app.route('/users', methods=['POST'])
def createUser():
    newUser = request.json
    with lock:
        users.append(newUser)
    return jsonify(newUser), 201

# Rota para adicionar uma nova conta a um usuário existente
@app.route('/users/<user_id>/accounts', methods=['POST'])
def add_account(user_id):
    data = request.get_json()
    new_account = {
        "id": data["id"],
        "saldo": data["saldo"],
        "tipo": data["tipo"]
    }
    with lock:
        ids = []
        for item in users:
            ids.append(item['id'])
        if int(user_id) not in ids:
            return jsonify({'message': 'Usuário não encontrado!'}), 401
        for user in users:
            if user['id'] == int(user_id):
                user['contas'].append(new_account)
        return jsonify({'message': 'Conta adicionada com sucesso!'}), 201

# Rota para listar todos as contas
@app.route('/users/<int:user_id>/accounts', methods=['GET'])
def get_accounts(user_id):
    with lock:
        for item in users:
            if item['id'] == user_id:
                accounts = item['contas']
                return jsonify(accounts), 201
        return '', 401

@app.route('/users/<int:user_id>/accounts/<int:account_id>', methods=['GET'])
def get_account(user_id, account_id):
    with lock:
        user = find_user(user_id)
        if user:
            account = find_account(user, account_id)
            if account:
                return jsonify(account), 201
            return jsonify({'message': 'Conta não encontrada'}), 401
        return jsonify({'message': 'Cliente não encontrado'}), 401

# Função auxiliar para encontrar uma conta por ID dentro de um cliente
def find_account(user, account_id):
    return next((account for account in user['contas'] if account['id'] == account_id), None)

# Função auxiliar para encontrar um cliente por ID
def find_user(user_id):
    return next((user for user in users if int(user['id']) == user_id), None)

# Rota para excluir um usuário
@app.route('/users/<int:user_id>', methods=['DELETE'])
def deleteUser(user_id):
    global users
    with lock:
        users = [user for user in users if user['id'] != user_id]
    return jsonify({'message': 'User excluído com sucesso'}), 201

# Rota para atualizar um usuário existente
@app.route('/users/<int:user_id>', methods=['PUT'])
def updateAccount(user_id):
    with lock:
        user = next((user for user in users if user['id'] == user_id), None)
        if not user:
            return jsonify({'message': 'User não encontrado'}), 401

        dataUpdate = request.json
        user.update(dataUpdate)
    return jsonify(user), 201

@app.route('/users/<int:user_id>/accounts/<int:account_id>/deposit', methods=['POST'])
def deposit(user_id, account_id):
    data = request.get_json()
    valor = data['value']
    with lock:
        client = find_user(user_id)
        if client:
            account = find_account(client, account_id)
            if account:
                account['saldo'] += valor
                return jsonify(account), 201
            return jsonify({'message': 'Conta não encontrada'}), 401
        return jsonify({'message': 'Cliente não encontrado'}), 401

@app.route('/users/<int:user_id>/accounts/<int:account_id>/take', methods=['POST'])
def take(user_id, account_id):
    data = request.get_json()
    valor = data['value']
    with lock:
        client = find_user(user_id)
        if client:
            account = find_account(client, account_id)
            if account:
                if account['saldo'] >= valor:
                    account['saldo'] -= valor
                    return jsonify(account), 201
                else:
                    return jsonify({'message': 'Saldo insuficiente'}), 401
            return jsonify({'message': 'Conta não encontrada'}), 401
        return jsonify({'message': 'Cliente não encontrado'}), 401

# Rota para inicializar 2PC
@app.route('/sender', methods=['POST'])
def sender():
    with lock:
        transation = request.get_json()
        for client in users:
            accounts = client['contas'][0]
            if accounts['id'] == transation['id']:
                accounts['saldo'] += transation['value']
                transation['status'] = 'commit'
                return jsonify(transation),201
        transation['status'] = 'abort'
        return jsonify(transation), 401
    
# Rota para inicializar 2PC
@app.route('/abort', methods=['POST'])
def abort():
    with lock:
        transation = request.get_json()
        for client in users:
            accounts = client['contas'][0]
            if accounts['id'] == transation['id']:
                accounts['saldo'] -= transation['value']
                transation['status'] = 'abort'
                return jsonify(transation),201
        return jsonify(transation), 401
        
# Rota para inicializar 2PC
@app.route('/recipient', methods=['POST'])
def recipient():
    transation = request.get_json()
    for client in users:
        accounts = client['contas'][0]
        if accounts['id'] == transation['id_origin']:
            if accounts['saldo'] < transation['value']:
                transation['status'] = 'abort'
                return jsonify({'message': 'saldo insuficiente'}), 401
            else:
                with lock:
                    accounts['saldo'] -= transation['value'] 
                    transation['status'] = 'commit'
                    return jsonify(transation), 201
    return jsonify(transation), 401
        
def abort_transactions(transactions):
    for trans in transactions:
        if trans['status'] == 'commit':
            
            #if len(trans["id"]) == 7:
            #    url = f'http://{bank[:11] + str(trans["id"])[:1]}:8088/abort'
            #else:
            #    url = f'http://{bank[:11] + str(trans["id"])[:2]}:8088/abort'
            
            #comentar a linha de baixo no laboratorio e descomentar as de cima
            url = f'http://{bank[:10] + str(trans["id"])[:3]}:8088/abort'
            response = requests.post(url, json=trans)
            while response.status_code != 201:
                response = requests.post(url, json=trans)    

@app.route('/transfers', methods=['POST'])
def receiveTransfers():
    try:
        data = request.get_json()
        if data is None:
            raise ValueError("Nenhum dado JSON fornecido")
        # Obtendo a primeira chave do dicionário
        primeira_chave = next(iter(data))

        # Obtendo o valor associado à primeira chave
        valor_primeira_chave = data[primeira_chave]
        transfers.append(valor_primeira_chave)
        finalizedTransfers.append([primeira_chave,""])
        return jsonify({"message": "ok"}), 201
    except Exception as e:
        return jsonify({"message": "erro"}), 401

def transfer(transations):
    trans_destiny = []
    trans_origin = []
    print(transations)
    for transation in transations:
        
        #if len(transation["id_destiny"]) == 7:
        #    url_destiny = f'http://{bank[:11] + str(transation["id_destiny"])[:1]}:8088/sender'
        #else:
        #    url_destiny = f'http://{bank[:11] + str(transation["id_destiny"])[:2]}:8088/sender'
            
        #comentar a linha de baixo no laboratorio e descomentar as de cima
        url_destiny = f'http://{bank[:10] + str(transation["id_destiny"])[:3]}:8088/sender'
        try: 
            
            #if len(transation["id_origin"]) == 7:
            #    url_origin = f'http://{bank[:11] + str(transation["id_origin"])[:1]}:8088/sender'
            #else:
            #    url_origin = f'http://{bank[:11] + str(transation["id_origin"])[:2]}:8088/sender'
                
            #comentar a linha de baixo no laboratorio e descomentar as de cima
            url_origin = f'http://{bank[:10] + str(transation["id_origin"])[:3]}:8088/recipient'
            response = requests.post(url_origin, json=transation, timeout=1)
            if response.status_code != 201:
                abort_transactions(trans_destiny)
                abort_transactions(trans_origin)
                return False
            else:
                transation2 = {
                    'id': transation['id_origin'],
                    'value': -(transation['value']),
                    'status': 'commit'
                }
                trans_origin.append(transation2)
                transation1 = {
                    'id': transation['id_destiny'],
                    'value': transation['value'],
                    'status': 'init'
                }
                response = requests.post(url_destiny, json=transation1, timeout=1)
                if response.status_code != 201:
                    abort_transactions(trans_destiny)
                    abort_transactions(trans_origin)
                    return False 
                else:
                    transation1['status'] = 'commit'
                    trans_destiny.append(transation1)
        except Exception as e:
            abort_transactions(trans_destiny)
            abort_transactions(trans_origin)
            return False
    return True

# Função para iniciar o servidor Flask
def init_server_flask():
    app.run(host='0.0.0.0', port=8088, threaded=True)

def main():
    
    # Inicia o servidor Flask em uma nova thread
    thread_servidor_flask = threading.Thread(target=init_server_flask)
    thread_servidor_flask.start()
    
    # Inicializa o nó com o token (apenas para o primeiro nó na rede)
    if node_state["node_id"] == 1:
        receive_token()
        node_state["pass"] == True
    
    # Inicializa a thread que verifica e passa o token periodicamente
    token_thread_pass = threading.Thread(target=pass_token)
    token_thread_pass.start()
    
    # Inicializa a thread que verifica e gera o token periodicamente
    token_thread = threading.Thread(target=check_token)
    token_thread.start()

if __name__ == '__main__':
    main()