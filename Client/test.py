import requests
import json
import threading
import random
import string
import json

bank = "172.16.103.8"

def sendTransaction(dataAccount, address):
    try:
        url = f'http://{bank[:11] + str(address)[:1]}:8088/transfers'
        print(f"Data: {dataAccount}")

        response = requests.post(url, json=dataAccount)

        # Checa se a resposta foi bem sucedida
        if response.status_code == 201:
            print("Transferência realizada com sucesso")
        else:
            print(f"Falha na request. Status Code: {response.status_code}")
            
        return response

    except requests.exceptions.RequestException as e:
        print(f"Ocorreu um erro na requisição: {e}")

transfers = [
    {"100000": # mudar na hora
    [{
    "id_destiny": 104100002,
    "id_origin": 103100000,
    "status": "init",
    "value": 25
    }]
    }, 
    {"100001": # mudar na hora
    [{
    "id_destiny": 104100002,
    "id_origin": 104100001,
    "status": "init",
    "value": 25
    }]
    }
]

addressToSend = [104100001, 103100000]

threads = []


# =========================================================================================================== #
# TESTE 1

# Este teste realiza duas operações em uma mesma conta a partir de contas diferentes
# Permite testar a passagem do token
# Mostra que duas transações "simultâneas" tendo como "alvo" uma mesma conta não gera inconsistências

# conta A pra B 
thread = threading.Thread(target=sendTransaction, args=(transfers[0], addressToSend[1], ))
threads.append(thread)

# conta C (outro banco) pra B
thread = threading.Thread(target=sendTransaction, args=(transfers[1], addressToSend[0], ))
threads.append(thread)

# =========================================================================================================== #
# TESTE 2

# Este teste realiza duas operações simultâneas usando a API de um mesmo banco
# Permite mostrar que o sistema trata situações em que duas operações ou mais ocorrem no mesmo banco (locks e fila)

# conta A pra B 
thread = threading.Thread(target=sendTransaction, args=(transfers[1], addressToSend[0], ))
threads.append(thread)

# conta A pra B 
thread = threading.Thread(target=sendTransaction, args=(transfers[1], addressToSend[0], ))
threads.append(thread)


for t in threads:
    t.start()

for thread in threads:
    thread.join()
