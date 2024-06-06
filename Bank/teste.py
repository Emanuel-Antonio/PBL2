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

# Rota para listar todos os usuários do Banco
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
    return jsonify({'message': 'User não encontrado'}), 404

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
            return jsonify({'message': 'Usuário não encontrado!'}), 404
        for user in users:
            if user['id'] == int(user_id):
                user['contas'].append(new_account)
        return jsonify({'message': 'Conta adicionada com sucesso!'}), 200

# Rota para listar todos as contas
@app.route('/users/<int:user_id>/accounts', methods=['GET'])
def get_accounts(user_id):
    with lock:
        for item in users:
            if item['id'] == user_id:
                accounts = item['contas']
                return jsonify(accounts)
        return '', 404

@app.route('/users/<int:user_id>/accounts/<int:account_id>', methods=['GET'])
def get_account(user_id, account_id):
    with lock:
        user = find_user(user_id)
        if user:
            account = find_account(user, account_id)
            if account:
                return jsonify(account)
            return jsonify({'message': 'Conta não encontrada'}), 404
        return jsonify({'message': 'Cliente não encontrado'}), 404

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
            return jsonify({'message': 'User não encontrado'}), 404

        dataUpdate = request.json
        user.update(dataUpdate)
    return jsonify(user)

if __name__ == "__main__":
    # Inicia a aplicação Flask
    app.run(host='0.0.0.0', port=8088, debug=True)
