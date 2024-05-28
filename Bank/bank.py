from api import app
import threading
import os
import json
import time
import requests

#bank = os.getenv("bank")
#bank = "172.16.103.14"

#bank = os.getenv("bank")
bank = "192.168.1.105"

def request():
    global bank
    url_consume = f'http://{bank}:8088/requests'  # Rota para consumir a API
    while True:
        try:    
            time.sleep(1)
            # Consumir a API para obter a mensagem recém-publicada
            response_consume = requests.get(url_consume)
            # Verificar se a mensagem foi consumida com sucesso
            if response_consume.status_code == 200:
                consumed_message = response_consume.json()
                if len(consumed_message) > 0: 
                    print(consumed_message[0]) 
                    valor = getUsers(consumed_message[0]['destino'])
                    if consumed_message[0]['tipo'] == 'deposito':
                        valor = valor['saldo'] + consumed_message[0]['valor']
                        updateUser(valor, consumed_message[0]['destino'])
                        print(valor)
                    elif consumed_message[0]['tipo'] == 'saque':
                        valor = valor['saldo'] - consumed_message[0]['valor']
                        updateUser(valor, consumed_message[0]['destino'])
                        print(valor)
                    requestRemove(consumed_message[0]['destino'])
        except Exception as e:
            print('Erro ao enviar/receber dados para/de API:', e)
            pass

def requestRemove(request):
    global bank
    url_delete = 'http://{}:8088/requests/{}'.format(bank,request)
    try:
        # Enviar requisição DELETE para remover o dado da API
        response_delete = requests.delete(url_delete)

        # Verificar se a remoção foi bem-sucedida
        if response_delete.status_code == 200:
            print("Requisição removida com sucesso da API.")
        else:
            print("Erro ao remover a requisição da API:", response_delete.status_code)
            return
    except Exception as e:
        print('Erro ao enviar/receber dados para/de API:', e)

def updateUser(valor, id):
    global bank
    url_update = 'http://{}:8088/user/{}'.format(bank,id)
    try:
        # Preparar os dados para atualizar na API
        payload = {'saldo': valor}
        json_payload = json.dumps(payload)
        headers = {'Content-Type': 'application/json'}

        # Enviar requisição PUT para atualizar o dado na API
        response_update = requests.put(url_update, data=json_payload, headers=headers)

        # Verificar se a atualização foi bem-sucedida
        if response_update.status_code == 200:
            print("Dado atualizado com sucesso na API.")
        else:
            print("Erro ao atualizar o dado na API:", response_update.status_code)
            return
    except Exception as e:
        print('Erro ao enviar/receber dados para/de API:', e)

def getUsers(id):
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

def main():

    try:
        # Inicia os servidores TCP e UDP em threads separadas
        thread = threading.Thread(target=request)
        thread.start()

        # Inicia a aplicação Flask
        app.run(host='0.0.0.0', port=8088, debug=True)

    except Exception as e:
        print('Erro:', e)

if __name__ == "__main__":
    main()