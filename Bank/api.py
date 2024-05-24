from flask import Flask, request, jsonify

app = Flask(__name__)

# Lista de usuários
dispositivos = []

requisicoes = []

# Rota para listar todos os usuários
@app.route('/dispositivos', methods=['GET'])
def get_usuarios():
    return jsonify(dispositivos)

@app.route('/requisicoes', methods=['GET'])
def get_requisicoes():
    return jsonify(requisicoes)

# Rota para obter um usuário por ID
@app.route('/dispositivos/<int:dispositivo_id>', methods=['GET'])
def get_usuario(dispositivo_id):
    dispositivo = next((dispositivo for dispositivo in dispositivos if dispositivo['id'] == dispositivo_id), None)
    if dispositivo:
        return jsonify(dispositivo)
    return jsonify({'message': 'Sensor não encontrado'}), 404

# Rota para criar um novo usuário
@app.route('/dispositivos', methods=['POST'])
def criar_usuario():
    novo_dispositivo = request.json
    novo_dispositivo['id'] = len(dispositivos) + 1
    dispositivos.append(novo_dispositivo)
    return jsonify(novo_dispositivo), 201

# Rota para criar um novo usuário
@app.route('/requisicoes', methods=['POST'])
def criar_requisicao():
    nova_requisicao = request.json
    nova_requisicao['id'] = len(requisicoes) + 1
    requisicoes.append(nova_requisicao)
    return jsonify(nova_requisicao), 201

# Rota para atualizar um usuário existente
@app.route('/dispositivo/<int:dispositivo_id>', methods=['PUT'])
def atualizar_usuario(dispositivo_id):
    dispositivo = next((dispositivo for dispositivo in dispositivos if dispositivo['id'] == dispositivo_id), None)
    if not dispositivo:
        return jsonify({'message': 'Sensor não encontrado'}), 404
    dados_atualizados = request.json
    dispositivo.update(dados_atualizados)
    return jsonify(dispositivo)

# Rota para excluir um usuário
@app.route('/dispositivo/<int:dispositivo_id>', methods=['DELETE'])
def excluir_usuario(dispositivo_id):
    global dispositivos
    dispositivos = [dispositivo for dispositivo in dispositivos if dispositivo['id'] != dispositivo_id]
    return jsonify({'message': 'Dispositivo excluído com sucesso'})

# Rota para excluir um usuário
@app.route('/requisicoes/<int:requisicao_id>', methods=['DELETE'])
def excluir_requisicao(requisicao_id):
    global requisicoes
    requisicoes = [requisicao for requisicao in requisicoes if requisicao['id'] != requisicao_id]
    return jsonify({'message': 'Dispositivo excluído com sucesso'})

if __name__ == "__main__":
    # Inicia a aplicação Flask
    app.run(host='0.0.0.0', port=8088, debug=True)