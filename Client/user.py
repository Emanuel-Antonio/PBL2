import os
import requests
import json
import random
import time
bank = "172.16.103.8"

#bank = os.getenv("bank")
#bank = "172.16.103.14"

def login(users):
    global bank
    limpar_terminal()
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
        verificarLogin(cod, password)
        return getUser(cod)
    else:
        name = input("Seu nome: ")
        age = int(input("Sua Idade: "))
        password = input("Sua senha: ")
        id = input("Digite seu Id: ")
        tipo = input('Digite o tipo de conta: ')
        
        if len(bank) == 12:
            pix = bank[-1:] + str(getTransId())
        else:
            pix = bank[-2:] + str(getTransId())
            
        #No laboratório comentar a linha a baixo e descomentar as de cima
        #pix = bank[-3:] + str(getTransId())

        createAccount(id, name, age, password, tipo, int(pix))
        return [id, name, age, password, tipo, int(pix)]
                
def createAccount(id, name, age, password, tipo, pix):
    global bank
    url_publish = f"http://{bank}:8088/users"
    try:
        # Preparar os dados para publicar na API
        payload = {
            'id': id,
            'nome': name,
            'idade': age,
            'senha': password,
            'contas': [{'id': pix, 'saldo': 0, 'tipo': tipo}]
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
    url_publish = f"http://{bank}:8088/login"
    try:
        # Preparar os dados para publicar na API
        payload = {
            'id': str(id),
            'password': str(password),
        }
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code != 201:
            print("Falha no login:", response_publish.status_code)
            print("Resposta da API:", response_publish.text)
        else:
            print("Login efetuado com sucesso!")
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
        if response_consume.status_code == 201:
            consumed_messsage = response_consume.json()
        else:
            print("Usuário inexistente!:", response_consume.status_code)
    except Exception as e:
        print("Não foi possível estabelescer uma conexão com o bank ...")
    return consumed_messsage        
    
def logged(user):
    while True:  
        limpar_terminal()
        try:
            user = getUser(user['id'])
            print(f"==============================================================\nTitular: {user['nome']}\nSaldo: {user['contas'][0]['saldo']}\nChave Pix: {user['id']}")
        except Exception as e:  
            user = getUser(user[0])
            print(f"==============================================================\nTitular: {user['nome']}\nSaldo: {user['contas'][0]['saldo']}\nChave Pix: {user['id']}")
        print("=============================menu=============================\n1 - Para Depositar; 2 - Para Sacar e 3 Para realizar transação\n==============================================================")
        opcao = int(input("==> "))
        if opcao == 1:
            valor = float(input("Digite o valor a Depositar: "))
            requestDeposito(valor, user['id'], user['contas'][0]['id'])
        elif opcao == 2:
            valor = float(input("Digite o valor a Sacar: "))
            requestSaque(valor, user['id'], user['contas'][0]['id'])
        elif opcao == 3:
            transacao = {}
            id = getTransId()
            transacao[str(id)] = []
            while True:
                print("=====================================\n1 Para adicionar micro-transação\n2 Para executar conjunto de transações\n=====================================")
                opcao = int(input())
                if opcao == 1:
                    m = {}
                    origem = int(input("Digite o id de origem: "))
                    destino = int(input("Digite o id de destino: "))
                    value = float(input("Digite o valor: "))
                    m["id_destiny"] = destino
                    m["id_origin"] = origem
                    m["status"] = "init"
                    m["value"] = value
                    transacao[str(id)].append(m)
                    print(transacao)
                else:
                    print(user['contas'][0]['id'])
                    requestTransferencia(transacao, user['contas'][0]['id'])
                    time.sleep(7)
                    verStatus(id)
                    break
        elif opcao == 4:
            break

def verStatus(id):
    global bank
    url_publish = f'http://{bank}:8088/status'

    try:
        
        # Preparar os dados para publicar na API
        payload = {'id': id}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}
        # Publicar na API
        response_publish = requests.get(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            print("Transação concluida com sucesso!")
            return
        else:
            print("Transação cancelada!") 
            return           
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Bank ...')
        return 

def getTransId():
    global bank
    url_publish = f'http://{bank}:8088/id'

    try:
        
        # Publicar na API
        response_publish = requests.get(url_publish,timeout=2)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            return response_publish.json()
        else:
            return
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Bank ...')
        return 

def requestSaque(valor, id, conta):
    global bank
    url_publish = f'http://{bank}:8088/users/{id}/accounts/{conta}/take'

    try:
        # Preparar os dados para publicar na API
        payload = {'value': valor}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            pass
        else:
            return
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Bank ...')
    
def requestDeposito(valor, id, conta):
    global bank
    url_publish = f'http://{bank}:8088/users/{id}/accounts/{conta}/deposit'
    print(url_publish)
    try:
        # Preparar os dados para publicar na API
        payload = {'value': valor}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            print('Operação efetuada com sucesso!')
        else:
            return
    except Exception as e:
        print('Não foi possível estabelecer uma conexão com o Bank ...')
    
def requestTransferencia(dic, id_origem):
    global bank
    
    if len(str(id_origem)) == 7:
        url_publish = f'http://{bank[:11] + str(id_origem)[:1]}:8088/transfers'
    else:
        url_publish = f'http://{bank[:11] + str(id_origem)[:2]}:8088/transfers'
    
    #comentar a de baixo e descomentar os de cima ao testar no laboratorio
    #url_publish = f'http://{bank[:10] + str(id_origem)[:3]}:8088/transfers'
    try:
        # Preparar os dados para publicar na API
        payload = dic  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, timeout=2, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            pass
        else:
            return
    except Exception as e:
        print(f'Não foi possível estabelecer uma conexão com o Bank ... {e}')

def limpar_terminal():
    # Verifica se o sistema operacional é Windows
    if os.name == 'nt':
        os.system('cls')  # Limpa o terminal no Windows
    else:
        # Limpa o terminal em sistemas Unix (Linux, macOS, etc.)
        os.system('clear') 

def main():
    while True:
        user = login(getUsers())
        if user != None:
            logged(user)
        
if __name__=="__main__":
    main()