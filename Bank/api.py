from flask import Flask, request, jsonify
import requests
import json
import os
from threading import Lock

app = Flask(__name__)

# bank = "172.16.103.14"
# bank = os.getenv("bank")
bank = "192.168.1.105"

# Lista de usuários
users = []
# Lock para sincronização
lock = Lock()

# Rota para listar todos os usuários
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/deposito', methods=['POST'])
def get_deposito():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No JSON data provided"}), 400

    with lock:
        for item in users:
            if item['id'] == data['destino']:
                item['saldo'] += data['valor']
    return '', 204

@app.route('/saque', methods=['POST'])
def get_saque():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No JSON data provided"}), 400

    with lock:
        for item in users:
            if item['id'] == data['destino']:
                if item['saldo'] < data['valor']:
                    return jsonify({"message": "Saldo insuficiente para realizar essa operacao"}), 404
                item['saldo'] -= data['valor']
    return '', 204

@app.route('/transferencia', methods=['POST'])
def get_transferencia():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No JSON data provided"}), 400

    url_publish = f'http://{bank[:10] + str(data["destino"])[:3]}:8088/receber'
    
    with lock:
        for item in users:
            if item['id'] == data['origem']:
                if data['valor'] > item['saldo']:
                    return jsonify({"message": "Saldo insuficiente para realizar a operacao"}), 404

    try:
        payload = {'destino': data['destino'], 'valor': data['valor'], 'tipo': 'transferencia', 'origem': data['origem']}  
        json_payload = json.dumps(payload)  
        headers = {'Content-Type': 'application/json'}

        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        if response_publish.status_code == 204:
            with lock:
                for item in users:
                    if item['id'] == data['origem']:
                        item['saldo'] -= data['valor']
            return '', 204
        else:
            response_json = response_publish.json()
            error_message = response_json.get('error', 'Unknown error')
            return jsonify({"message": "{}".format(error_message)}), 404
    except Exception as e:
        print(f'Não foi possível estabelecer uma conexão com o Broker ... {e}')
        return jsonify({"message": "Erro na conexão com o Broker"}), 500

@app.route('/receber', methods=['POST'])
def get_receber():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No JSON data provided"}), 400

    with lock:
        for item in users:
            if item['id'] == data['destino']:
                item['saldo'] += data['valor']
                return '', 204
    return jsonify({"message": "Conta inexistente"}), 404

# Rota para obter um usuário por ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({'message': 'Sensor não encontrado'}), 404

# Rota para criar um novo usuário
@app.route('/users', methods=['POST'])
def createUser():
    newUser = request.json
    with lock:
        users.append(newUser)
    return jsonify(newUser), 201

# Rota para atualizar um usuário existente
@app.route('/user/<int:user_id>', methods=['PUT'])
def updateUser(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if not user:
        return jsonify({'message': 'User não encontrado'}), 404

    dataUpdate = request.json
    with lock:
        user.update(dataUpdate)
    return jsonify(user)

# Rota para excluir um usuário
@app.route('/user/<int:user_id>', methods=['DELETE'])
def deleteUser(user_id):
    global users
    with lock:
        users = [user for user in users if user['id'] != user_id]
    return jsonify({'message': 'User excluído com sucesso'})

if __name__ == "__main__":
    # Inicia a aplicação Flask
    app.run(host='0.0.0.0', port=8088, debug=True)
