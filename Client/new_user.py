import os
import requests
import json
import random
bank = "192.168.1.105"

#bank = os.getenv("bank")
#bank = "172.16.103.14"

def login(users):
    global bank
    print("------------------------------")
    print(" 1 - Entrar\n 2 - Criar conta\n ")
    opcao = int(input("===>"))
    codUtilizado = []
    for item in users:
        codUtilizado.append(item['id'])
    print("------------------------------")
    while opcao < 1 or opcao > 2:
        print("Escreva uma opção válida!\n")
        opcao = int(input("==>"))
        print("------------------------------")
    if opcao == 1:
        cod = input("Digite o código da conta\n==>\n")
        password = input("Digite a senha\n==>\n")
        verificarLogin(int(cod), password)
        return getUser(cod)
    else:
        name = input("Seu nome: ")
        age = int(input("Sua Idade: "))
        password = input("Sua senha: ")
        id = input("Digite seu Id")
        tipo = input('Digite o tipo de conta')
        createAccount(id, name, age, password, tipo)
        return Client(name, age, password, id, 0)
                
def createAccount(id, name, age, password, tipo):
    global bank
    url_publish = f"http://{bank}:8088/users"
    try:
        # Preparar os dados para publicar na API
        payload = {
            'id': id,
            'nome': name,
            'idade': age,
            'senha': password,
            'contas': [{'id': int(bank[10:]), 'saldo': 0, 'tipo': tipo}]
        }
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            print("Conta criada com sucesso!")
        else:
            print("Erro ao enviar os dados UDP para a API:", response_publish.status_code)
            print("Resposta da API:", response_publish.text)
    except Exception as e:
        print("Erro:", e)
        print('Não foi possível estabelecer uma conexão com o bank ...')
        
def verificarLogin(id, password):
    global bank
    url_publish = f"http://{bank}:8088/users"
    try:
        # Preparar os dados para publicar na API
        payload = {
            'id': id,
            'senha': password,
        }
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            print("Login efetuado com sucesso!")
        else:
            print("Erro ao enviar os dados UDP para a API:", response_publish.status_code)
            print("Resposta da API:", response_publish.text)
    except Exception as e:
        print("Erro:", e)
        print('Não foi possível estabelecer uma conexão com o bank ...')
        
def addBank(id, saldo, password):
    global bank
    url_publish = f"http://{bank}:8088/add_bank/{id}"
    try:
        # Preparar os dados para publicar na API
        payload = {'bank': bank, "balance": saldo, "password": password}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            pass
        else:
            print("Erro ao enviar os dados UDP para a API:", response_publish.status_code)
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o bank ...')
        
def getUsers():
    global bank
    url_consume = f"http://{bank}:8088/users"
    consumed_messsage = {}
    try:
        response_consume = requests.get(url_consume, timeout=2)
        if response_consume.status_code == 200:
            consumed_messsage = response_consume.json()
        else:
            print("Erro ao consumir a API:", response_consume.status_code)
    except Exception as e:
        print("Não foi possível estabelescer uma conexão com o bank ...")
    return consumed_messsage   
     
def getUser(id):
    global bank
    url_consume = f"http://{bank}:8088/users/{id}"
    consumed_messsage = {}
    try:
        response_consume = requests.get(url_consume, timeout=2)
        if response_consume.status_code == 200:
            consumed_messsage = response_consume.json()
        else:
            print("Erro ao consumir a API:", response_consume.status_code)
    except Exception as e:
        print("Não foi possível estabelescer uma conexão com o bank ...")
    return consumed_messsage        
    
def logged(user):
    while True:
        print(user)
        opcao = int(input("==> "))
        if opcao == 1:
            print('')
        elif opcao == 2:
            print('')
        elif opcao == 3:
            print('')
        elif opcao == 4:
            break

def requestSaque(valor, cliente):
    global bank
    url_publish = f'http://{bank}:8088/saque'

    try:
        # Preparar os dados para publicar na API
        payload = {'destino': cliente.id, 'valor': valor, 'tipo': 'saque'}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 204:
            pass
        else:
            response_json = response_publish.json()
            error_message = response_json.get('message', 'Unknown error')
            print("Erro ao enviar os dados UDP para a API:", error_message)            
            return
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Broker ...')
    
def requestDeposito(valor, cliente):
    global bank
    url_publish = f'http://{bank}:8088/deposito'

    try:
        # Preparar os dados para publicar na API
        payload = {'destino': cliente.id, 'valor': valor, 'tipo': 'deposito'}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 204:
            print('Operação efetuada com sucesso!')
        else:
            response_json = response_publish.json()
            error_message = response_json.get('message', 'Unknown error')
            print("Erro ao enviar os dados UDP para a API:", error_message)
            return
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Bank ...')
    
def requestTransferencia(cod, cliente, valor):
    # desenvolver depois
    global bank
    url_publish = f'http://{bank[:10] + str(cod[:3])}:8088/transferencia'

    try:
        # Preparar os dados para publicar na API
        payload = {'destino': int(cod), 'valor': valor, 'tipo': 'transferencia', 'origem': cliente.id}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 204:
            pass
        else:
            response_json = response_publish.json()
            error_message = response_json.get('message', 'Unknown error')
            print("Erro ao enviar os dados UDP para a API:", error_message)
            return
    except Exception as e:
        print(f'Não foi possível estabelecer uma conexão com o Broker ... {e}')

def main():
    while True:
        user = login(getUsers())
        if user != False:
            logged(user)
        
if __name__=="__main__":
    main()