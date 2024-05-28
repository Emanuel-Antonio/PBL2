from client import *
import os
import requests
import json
import random

#bank = os.getenv("bank")
bank = "192.168.1.105"

def login(users):
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
        cod = int(input("Digite o código da conta\n==>\n"))
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
        while id in codUtilizados:
            id = random.randint(100000, 999999)
        createAccount(id, name, age, passwor)
        return Client(name, age, passwor, id, 0.0)

                
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
    
def sendRequest():
    print("")       
     
def logged(cliente):
    while True:
        cliente
        print(f"------------------------------\nTitular: {cliente.nome}\nSaldo: {cliente.saldo}\n\nPara Deposito digite 1:\nPara Saque digite 2:\nPara Transferir digite 3\nPara Sair digite 4")
        opcao = int(input("==> "))
        if opcao == 1:
            cliente
        elif opcao == 2:
            pass
        elif opcao == 3:
            break

def loggedAdmin(cliente, banks):
    while True:
        cliente
        print(f"------------------------------\nTitular: {cliente.nome}\nSaldo: {cliente.saldo}\n\nPara Adicionar outro Banco digite 1\nPara Sair digite 2")
        opcao = int(input("==> "))
        if opcao == 1:
            print('Digite o endereco MAC do servidor\n')
            mac = input("==> ")
            print('Digite o apelido sendo um número de 2 digitos\n')
            apelido = input("==>")
            print('Confirme a operação com a sua senha\n')
            senha = input("==>")
            if senha == cliente.password:
                banks[apelido] = mac
                return banks
            else:
                print("Operação cancelada devido a senha estar incorreta")
        elif opcao == 2:
            return banks

def requestSaque():
    print('')
    
def requestDeposito():
    print('')
    
def requestTransferencia():
    print('')

def main():
    users = []
    users = getUsers()
    banks = {}
    while True:
        cliente = login(users)
        if cliente != False:
            if users[0]['id'] == cliente.id:
                banks = loggedAdmin(cliente, banks)
            else:
                logged(cliente)
        print(banks)

        
if __name__=="__main__":
    main()
    

    
    
