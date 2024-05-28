from client import *
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
    codUtilizados = []
    for item in users:
        codUtilizados.append(item['id'])
    print("------------------------------")
    while opcao < 1 or opcao > 2:
        print("Escreva uma opção válida!\n")
        opcao = int(input("==>"))
        print("------------------------------")
    if opcao == 1:
        cod = input("Digite o código da conta\n==>\n")
        password = input("Digite a senha\n==>\n")
        for user in users:
            if (cod == user['id']) and (password == user['senha']):
                cliente = Client(user['nome'], user['idade'], user['senha'], user['id'], user['saldo'])
                print("Login efetuado com sucesso")
                return cliente
        else:
            print("Usuário ou senha inválido!\n Tente acessar uma conta existente ou crie uma conta")
            return False   
    else:
        name = input("Seu nome: ")
        age = int(input("Sua Idade: "))
        passwor = input("Sua senha: ")
        id = random.randint(100000, 999999)
        while int(bank[10:]+str(id)) in codUtilizados:
            id = random.randint(100000, 999999)
        createAccount(int(bank[10:]+str(id)), name, age, passwor)
        return Client(name, age, passwor, int(bank[10:]+str(id)), 0.0)

                
def createAccount(id, name, age, password):
    global bank
    url_publish = f"http://{bank}:8088/users"
    try:
        # Preparar os dados para publicar na API
        payload = {'id': id, 'nome': name, 'idade': age, 'senha': password, 'saldo': 0.0}  # Supondo que data_udp é uma sequência de bytes
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
     
def logged(cliente):
    while True:
        cliente
        print(f"------------------------------\nTitular: {cliente.nome}\nSaldo: {cliente.saldo}\n\nPara Deposito digite 1:\nPara Saque digite 2:\nPara Transferir digite 3\nPara Sair digite 4")
        opcao = int(input("==> "))
        if opcao == 1:
            valor = float(input("Digite o valor a ser depositado: "))
            senha = input("Digite a senha para confirmar: ")
            if (senha == cliente.password):
                requestDeposito(valor, cliente)
            else:
                print('Operação invalidada!')#senha errada
        elif opcao == 2:
            valor = float(input("Digite o valor a ser retirado:  "))
            senha = input("Digite a senha para confirmar: ")
            if (senha == cliente.password):
                requestSaque(valor, cliente)
            else:
                print('Operação invalidada!')#senha errada
        elif opcao == 3:
            valor = float(input("Digite o valor a ser transferido:  "))
            cod = input("Digite o código da conta: ")
            senha = input("Digite a senha para confirmar: ")
            if (senha == cliente.password):
                requestTransferencia(cod, valor)
            else:
                print('Operação invalidada!')#senha errada
        elif opcao == 4:
            break

def requestSaque(valor, cliente):
    global bank
    url_publish = f'http://{bank}:8088/requests'

    try:
        # Preparar os dados para publicar na API
        payload = {'destino': cliente.id, 'valor': valor, 'tipo': 'saque'}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            pass
        else:
            print("Erro ao enviar os dados UDP para a API:", response_publish.status_code)
            return
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Broker ...')
    
def requestDeposito(valor, cliente):
    global bank
    url_publish = f'http://{bank}:8088/requests'

    try:
        # Preparar os dados para publicar na API
        payload = {'destino': cliente.id, 'valor': valor, 'tipo': 'deposito'}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            print('Operação efetuada com sucesso!')
        else:
            print("Erro ao enviar a requisição para a API:", response_publish.status_code)
            return
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Bank ...')
    
def requestTransferencia():
    # desenvolver depois
    global bank
    url_publish = f'http://{bank}:8088/requests'

    try:
        # Preparar os dados para publicar na API
        payload = {'destino': '', 'origem': ''}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            pass
        else:
            print("Erro ao enviar os dados UDP para a API:", response_publish.status_code)
            return
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Broker ...')

def main():
    users = []
    users = getUsers()
    while True:
        cliente = login(users)
        if cliente != False:
            logged(cliente)
        
if __name__=="__main__":
    main()