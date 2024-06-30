from flask import Flask, request, jsonify
import requests
import threading
import time

app = Flask(__name__)

# Configurações de rede - altere esses IPs para os IPs das suas duas máquinas
ips = ["http://192.168.1.103:8081", "http://192.168.1.104:8081"]
indice_ip_atual = 1
ip = "192.168.1.104"

# Variável global para indicar se a máquina possui o token
tem_token = False
sequencia_token = 0  # Sequência do token
timeout_token = 30  # Tempo máximo de espera pelo token em segundos
conectado = True

# Estrutura de dados para armazenar clientes e suas contas
clientes = []
lock = threading.Lock()

# Estrutura de dados para armazenar as transferencias
transferencias = []
transferencias_finalizadas = []

# Função auxiliar para encontrar um cliente por ID
def find_cliente(cliente_id):
    return next((cliente for cliente in clientes if cliente['id'] == cliente_id), None)

# Função auxiliar para encontrar uma conta por ID dentro de um cliente
def find_conta(cliente, conta_id):
    return next((conta for conta in cliente['contas'] if conta['id'] == conta_id), None)

# Rotas para clientes
@app.route('/clientes', methods=['GET'])
def get_clientes():
    with lock:
        clientes_sem_senha = [cliente.copy() for cliente in clientes]
        for cliente in clientes_sem_senha:
            del cliente['senha']
        return jsonify(clientes_sem_senha)

@app.route('/clientes/<int:cliente_id>', methods=['GET'])
def get_cliente(cliente_id):
    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            cliente_sem_senha = cliente.copy()
            del cliente_sem_senha['senha']
            return jsonify(cliente_sem_senha)
        return jsonify({'message': 'Cliente não encontrado'}), 404

@app.route('/clientes', methods=['POST'])
def criar_cliente():
    novo_cliente = request.json
    required_fields = ['id', 'nome', 'idade', 'senha']
    
    for field in required_fields:
        if field not in novo_cliente:
            return jsonify({'message': f'Campo obrigatório {field} está faltando'}), 400

    with lock:
        if find_cliente(novo_cliente['id']):
            return jsonify({'message': 'Cliente com este ID já existe'}), 400
        novo_cliente['contas'] = []
        clientes.append(novo_cliente)
        cliente_sem_senha = novo_cliente.copy()
        del cliente_sem_senha['senha']
        return jsonify(cliente_sem_senha), 201

@app.route('/clientes/<int:cliente_id>', methods=['DELETE'])
def excluir_cliente(cliente_id):
    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            clientes.remove(cliente)
            return jsonify({'message': 'Cliente excluído com sucesso'})
        return jsonify({'message': 'Cliente não encontrado'}), 404

# Rotas para contas dentro de um cliente específico
@app.route('/clientes/<int:cliente_id>/contas', methods=['GET'])
def get_contas(cliente_id):
    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            return jsonify(cliente['contas'])
        return jsonify({'message': 'Cliente não encontrado'}), 404

@app.route('/clientes/<int:cliente_id>/contas/<int:conta_id>', methods=['GET'])
def get_conta(cliente_id, conta_id):
    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            conta = find_conta(cliente, conta_id)
            if conta:
                return jsonify(conta)
            return jsonify({'message': 'Conta não encontrada'}), 404
        return jsonify({'message': 'Cliente não encontrado'}), 404

@app.route('/clientes/<int:cliente_id>/contas', methods=['POST'])
def criar_conta(cliente_id):
    nova_conta = request.json
    required_fields = ['id', 'saldo']
    
    for field in required_fields:
        if field not in nova_conta:
            return jsonify({'message': f'Campo obrigatório {field} está faltando'}), 400

    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            if find_conta(cliente, nova_conta['id']):
                return jsonify({'message': 'Conta com este ID já existe para o cliente'}), 400
            cliente['contas'].append(nova_conta)
            return jsonify(nova_conta), 201
        return jsonify({'message': 'Cliente não encontrado'}), 404

@app.route('/clientes/<int:cliente_id>/contas/<int:conta_id>', methods=['PUT'])
def atualizar_conta(cliente_id, conta_id):
    dados_atualizados = request.json
    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            conta = find_conta(cliente, conta_id)
            if conta:
                conta.update(dados_atualizados)
                return jsonify(conta)
            return jsonify({'message': 'Conta não encontrada'}), 404
        return jsonify({'message': 'Cliente não encontrado'}), 404

@app.route('/clientes/<int:cliente_id>/contas/<int:conta_id>', methods=['DELETE'])
def excluir_conta(cliente_id, conta_id):
    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            cliente['contas'] = [conta for conta in cliente['contas'] if conta['id'] != conta_id]
            return jsonify({'message': 'Conta excluída com sucesso'})
        return jsonify({'message': 'Cliente não encontrado'}), 404

# Endpoint para depositar em uma conta
@app.route('/clientes/<int:cliente_id>/contas/<int:conta_id>/depositar', methods=['POST'])
def depositar(cliente_id, conta_id):
    valor_deposito = request.json.get('valor')
    
    if valor_deposito is None:
        return jsonify({'message': 'Campo obrigatório valor está faltando'}), 400

    if valor_deposito <= 0:
        return jsonify({'message': 'Valor de depósito deve ser maior que zero'}), 400

    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            conta = find_conta(cliente, conta_id)
            if conta:
                conta['saldo'] += valor_deposito
                return jsonify(conta)
            return jsonify({'message': 'Conta não encontrada'}), 404
        return jsonify({'message': 'Cliente não encontrado'}), 404

# Endpoint para depositar em uma conta
@app.route('/clientes/<int:cliente_id>/contas/<int:conta_id>/sacar', methods=['POST'])
def sacar(cliente_id, conta_id):
    valor_saque = request.json.get('valor')
    
    if valor_saque is None:
        return jsonify({'message': 'Campo obrigatório valor está faltando'}), 400

    with lock:
        cliente = find_cliente(cliente_id)
        if cliente:
            conta = find_conta(cliente, conta_id)
            if conta:
                if conta['saldo'] >= valor_saque:
                    conta['saldo'] -= valor_saque
                    return jsonify(conta), 200
                else:
                    return jsonify({'message': 'Saldo insuficiente'}), 404
            return jsonify({'message': 'Conta não encontrada'}), 404
        return jsonify({'message': 'Cliente não encontrado'}), 404
    
# Endpoint para login
@app.route('/login', methods=['POST'])
def login():
    dados_login = request.json
    cliente_id = dados_login.get('id')
    senha = dados_login.get('senha')

    if not cliente_id or not senha:
        return jsonify({'message': 'ID e senha são obrigatórios'}), 400

    with lock:
        cliente = find_cliente(cliente_id)
        if cliente and cliente['senha'] == senha:
            cliente_sem_senha = cliente.copy()
            del cliente_sem_senha['senha']
            return jsonify({'message': 'Login bem-sucedido', 'cliente': cliente_sem_senha})
        return jsonify({'message': 'ID ou senha incorretos'}), 401

# aqui preparo od dados para a transferencia e enviou se pode ou não ser feito 
@app.route('/receber', methods=['POST'])
def receber_transferencia():
    with lock:
        transferencia = request.get_json()
        for item in clientes:
            if item["id"] == transferencia["id"]:
                item['contas'][0]["saldo"] += transferencia['valor']
                transferencia["status"] = "preparado"
                return jsonify(transferencia), 201
        transferencia["status"] = "abortado"
        return jsonify(transferencia), 404

# aqui reverto a transferencia
@app.route('/reverter', methods=['POST'])
def reverter_transferencia():
    with lock:
        transferencia = request.get_json()
        print(transferencia)
        for item in clientes:
            print(item["id"])
            print(transferencia["id"])
            if item["id"] == transferencia["id"]:
                item['contas'][0]["saldo"] -= transferencia['valor']
                transferencia["status"] = "revertido"
                return jsonify(transferencia), 201
        return jsonify(transferencia), 404

@app.route('/preparar', methods=['POST'])
def preparar_transferencia():
    nova_transferencia = request.get_json()
    for item in clientes:
        if item["id"] == nova_transferencia["id_origem"]:
            if item["contas"][0]["saldo"] < nova_transferencia["valor"]:
                nova_transferencia["status"] = "abortado"
                return jsonify(nova_transferencia), 400

    # Deduz o saldo do remetente localmente
    for item in clientes:
        if item["id"] == int(nova_transferencia["id_origem"]):
            item["contas"][0]["saldo"] -= nova_transferencia["valor"]
            nova_transferencia["status"] = "preparado"
            return jsonify(nova_transferencia), 201

@app.route('/transferencias', methods=['POST'])
def receber_transferencias():
    try:
        transferencia = request.get_json()
        transferencias.append(transferencia)
        return jsonify({'message': 'Transferências recebidas com sucesso'}), 201
    except Exception as e:
        print(f"Erro ao receber transferências: {e}")
        return jsonify({'message': 'Erro ao receber transferências'}), 500

# Rota para obter transferências de um usuário específico
@app.route('/transferencias_finalizadas/usuario/<int:usuario_id>', methods=['GET'])
def get_transferencias_por_usuario(usuario_id):
    for i in transferencias_finalizadas:
        if i[0]["Usuario"] == usuario_id:
            transferencias_finalizadas.pop(0)
            return jsonify({'message': 'Transferência realizada'}), 201
    else:
        return jsonify({'message': 'Nenhuma transferência encontrada para este usuário'}), 404
    
def fazer_transferencia():
    global transferencias, ip
    lista_destino = []
    lista_origem = []

    for nova_transferencia in transferencias[0]:
        url_destino = f"http://{ip[:-3] + str(nova_transferencia["id_destino"])[-3:]}:8081/receber"
           
        try:
            url_origem = f"http://{ip[:-3] + str(nova_transferencia["id_origem"])[-3:]}:8081/preparar"
            print(url_origem)
            response = requests.post(url_origem, json=nova_transferencia, timeout=1)
            
            if response.status_code != 201:
                # Reverter dedução em caso de exceção
                for item in lista_destino:
                    if item["status"] == "preparado":
                        # Reverter dedução em caso de exceção
                        url_destino =  f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                        print(url_destino)
                        print(item,  "1")
                        response = requests.post(url_destino, json=item, timeout=1)
                        while response.status_code != 201:
                            url_destino =  f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                            print(url_destino)
                            print(item,  "1")
                            response = requests.post(url_destino, json=item, timeout=1)
                for item in lista_origem:
                    if item["status"] == "preparado":
                        # Reverter dedução em caso de exceção
                        url_origem = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                        print(url_origem)
                        print(item,  "1")
                        response = requests.post(url_origem, json=item, timeout=1)
                        while response.status_code != 201:
                            url_origem = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                            print(url_origem)
                            print(item,  "1")
                            response = requests.post(url_origem, json=item, timeout=1)
                return False

            transferencia = {
                "id": nova_transferencia['id_origem'],
                "valor": -(nova_transferencia['valor']),
                "status": response.json()["status"]
            } 
            lista_origem.append(transferencia)

            # Enviar solicitação para adicionar saldo ao destinatário
            transferencia2 = {
                "id": nova_transferencia['id_destino'],
                "valor": nova_transferencia['valor'],
                "status": "default"
            }

            response = requests.post(url_destino, json=transferencia2, timeout=1)

            if response.status_code != 201: 
                # Reverter dedução em caso de exceção
                for item in lista_destino:
                    if item["status"] == "preparado":
                        # Reverter dedução em caso de exceção
                        url_destino = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                        print(url_destino)
                        print(item,  "2")
                        response = requests.post(url_destino, json=item, timeout=1)
                        while response.status_code != 201:
                            url_destino = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                            print(url_destino)
                            print(item,  "2")
                            response = requests.post(url_destino, json=item, timeout=1)
                for item in lista_origem:
                    if item["status"] == "preparado":
                        # Reverter dedução em caso de exceção
                        url_origem = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                        print(url_origem)
                        print(item,  "2")
                        response = requests.post(url_origem, json=item, timeout=1)
                        while response.status_code != 201:
                            url_origem = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                            print(url_origem)
                            print(item,  "2")
                            response = requests.post(url_origem, json=item, timeout=1)
                return False
            else:
                transferencia2["status"] = "preparado"
                lista_destino.append(transferencia2)            
                
        except Exception as e:
            with lock:
                # Reverter dedução em caso de exceção
                for item in lista_destino:
                    if item["status"] == "preparado":
                        # Reverter dedução em caso de exceção
                        url_destino = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                        print(url_destino)
                        print(item,  "3")
                        response = requests.post(url_destino, json=item, timeout=1)
                        while response.status_code != 201:
                            url_destino = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                            print(url_destino)
                            print(item,  "3")
                            response = requests.post(url_destino, json=item, timeout=1)
                for item in lista_origem:
                    if item["status"] == "preparado":
                        # Reverter dedução em caso de exceção
                        url_origem = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                        print(url_origem)
                        print(item,  "3")
                        response = requests.post(url_origem, json=item, timeout=1)
                        while response.status_code != 201:
                            url_origem = f"http://{ip[:-3] + str(item["id"])[-3:]}:8081/reverter"
                            print(url_origem)
                            print(item,  "3")
                            response = requests.post(url_origem, json=item, timeout=1)
                return False
    return True

###################################################################
#                           Token ring                            #
###################################################################

@app.route('/token', methods=['POST'])
def receber_token():
    global tem_token, sequencia_token
    dados = request.get_json()
    sequencia_recebida = dados.get('sequencia', -1)
    
    if sequencia_recebida > sequencia_token:
        sequencia_token = sequencia_recebida
        tem_token = True
        print(f"Recebeu token com sequência {sequencia_token}")
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "sequência inválida"}), 400

@app.route('/verificar_token', methods=['GET'])
def verificar_token():
    global tem_token, sequencia_token
    return jsonify({"tem_token": tem_token, "sequencia": sequencia_token})

def passar_token():
    global indice_ip_atual, sequencia_token, ips, tem_token, ip, conectado
    conseguiu = False
    i = indice_ip_atual
    while True:
        i = ((i + 1) % len(ips))
        if ips[i] != ips[indice_ip_atual]:
            try:
                resposta = requests.post(f"{ips[i]}/token", json={"sequencia": sequencia_token + 1}, timeout=5)
                if resposta.status_code == 200:
                    conseguiu = True
                    print(f"Token passado para {ips[i]}")
                    break
                else:
                    print(f"Erro ao passar Token para {ips[i]}") 
            except requests.exceptions.RequestException as e:
                print(f"Erro ao conectar a {ips[i]}: {e}")
                pass
        else:
            if conseguiu == False:
                conectado = False
                tem_token = True
        
def iniciar_servidor(ip, porta):
    app.run(host=ip, port=porta)

def monitorar_token():
    global tem_token, timeout_token
    while True:
        try:
            if not tem_token:
                ultimo_tempo_token = time.time()
                while not tem_token:
                    time.sleep(1)
                    tempo_passado_token = time.time()
                    if (tempo_passado_token - ultimo_tempo_token) > timeout_token:
                        print("Tempo de espera do token excedido. Reeleição do token.")
                        reeleger_token()
                        break
        except:
            pass

def reeleger_token():
    global sequencia_token, ips
    try:
        sequencia_token = sequencia_token + len(ips)
        passar_token()
    except:
        print("Erro ao reeleger token!")

def iniciar():
    global sequencia_token, tem_token, ip, ips

    if f"http://{ip}:8081" == ips[0]:
        tem_token = True  # A primeira máquina começa com o token
        sequencia_token = 0

def processamento():
    global tem_token, transferencias, transferencias_finalizadas
    while True:
        if tem_token == True and conectado == True:
            # Simular recebimento de uma solicitação de processamento
            print("Máquina com token. Pronta para processar.")
            time.sleep(1)
            if  len(transferencias) != 0:
                retorno = fazer_transferencia()
                if retorno == True:
                    print("Transferencia realizada!")
                    transferencias_finalizadas.append(transferencias[0])
                    print(transferencias_finalizadas)
                else:
                    print("Erro ao realizar transferencia!")
                transferencias.pop(0)
            else:
                pass
            
            tem_token = False
            passar_token()
            
        elif tem_token == True and conectado == False:   
            tem_token = False
            passar_token()

def main():
    global tem_token, ip
    porta = 8081  # Porta fixa

    iniciar()

    thread_servidor = threading.Thread(target=iniciar_servidor, args=(ip, porta))
    thread_servidor.start()

    thread_monitor = threading.Thread(target=monitorar_token)
    thread_monitor.start()

    thread_process = threading.Thread(target=processamento)
    thread_process.start()

if __name__ == "__main__":
    main()
