from flask import Flask, request, jsonify
import requests
import json
import os
from threading import Lock

app = Flask(__name__)

# Configurações
#bank = os.getenv("bank")

bank = "192.168.1.105"

# Lista de usuários
users = []
# Lock para sincronização
lock = Lock()

# Rota para verificar login todos os usuários do Banco
@app.route('/login', methods=['POST'])
def set_login():
    data = request.get_json()
    user_id = data['id']
    password = data['password']
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
        return jsonify(users_no_password)

# Rota para obter um usuário por ID no Banco
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    with lock:
        users_no_password = [user.copy() for user in users]
        for user in users_no_password:
            del user['senha']
        user = next((user for user in users_no_password if user['id'] == user_id), None)
        if user:
            return jsonify(user)
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
                return jsonify(accounts)
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
    return next((user for user in users if user['id'] == user_id), None)

# Rota para excluir um usuário
@app.route('/users/<int:user_id>', methods=['DELETE'])
def deleteUser(user_id):
    global users
    with lock:
        users = [user for user in users if user['id'] != user_id]
    return jsonify({'message': 'User excluído com sucesso'})

# Rota para atualizar um usuário existente
@app.route('/users/<int:user_id>', methods=['PUT'])
def updateAccount(user_id):
    with lock:
        user = next((user for user in users if user['id'] == user_id), None)
        if not user:
            return jsonify({'message': 'User não encontrado'}), 401

        dataUpdate = request.json
        user.update(dataUpdate)
    return jsonify(user)

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
            url = f'http://{bank[:10] + str(trans["id"])[:3]}:8088/abort'
            response = requests.post(url, json=trans)
            while response.status_code != 201:
                response = requests.post(url, json=trans)    
        
# Rota para tranferir
@app.route('/transfer', methods=['POST'])
def transfer():
    transations = request.get_json()
    trans_destiny = []
    trans_origin = []
    for transation in transations:
        url_destiny = f'http://{bank[:10] + str(transation["id_destiny"])[:3]}:8088/sender'
        try: 
            url_origin = f'http://{bank[:10] + str(transation["id_origin"])[:3]}:8088/recipient'
            response = requests.post(url_origin, json=transation, timeout=1)
            if response.status_code != 201:
                abort_transactions(trans_destiny)
                abort_transactions(trans_origin)
                return jsonify({'message': 'Transação cancelada'}), 401
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
                    return jsonify({'message': 'Transação cancelada'}), 401 
                else:
                    transation1['status'] = 'commit'
                    trans_destiny.append(transation1)
        except Exception as e:
            abort_transactions(trans_destiny)
            abort_transactions(trans_origin)
            return jsonify({'message': 'Transação cancelada'}), 401 
    return jsonify({'message': 'Transação concluida'}), 201 

if __name__ == "__main__":
    # Inicia a aplicação Flask
    app.run(host='0.0.0.0', port=8088, debug=True)
