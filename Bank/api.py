from flask import Flask, request, jsonify

app = Flask(__name__)

# Lista de usuários
users = []

requests = []

# Rota para listar todos os usuários
@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/requests', methods=['GET'])
def get_requests():
    return jsonify(requests)

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
    users.append(newUser)
    return jsonify(newUser), 201

# Rota para criar um novo usuário
@app.route('/requests', methods=['POST'])
def createRequests():
    newRequests = request.json
    requests.append(newRequests)
    return jsonify(newRequests), 201

# Rota para atualizar um usuário existente
@app.route('/user/<int:user_id>', methods=['PUT'])
def updateUser(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if not user:
        return jsonify({'message': 'User não encontrado'}), 404
    dataUpdate = request.json
    user.update(dataUpdate)
    return jsonify(user)

# Rota para excluir um usuário
@app.route('/user/<int:user_id>', methods=['DELETE'])
def deleteUser(user_id):
    global users
    users = [user for user in users if user['id'] != user_id]
    return jsonify({'message': 'User excluído com sucesso'})

# Rota para excluir uma requisição
@app.route('/requests/<int:request_id>', methods=['DELETE'])
def deleteRequest(request_id):
    global requests
    requests = [request for request in requests if request['id'] != request_id]
    return jsonify({'message': 'Request excluído com sucesso'})

if __name__ == "__main__":
    # Inicia a aplicação Flask
    app.run(host='0.0.0.0', port=8088, debug=True)