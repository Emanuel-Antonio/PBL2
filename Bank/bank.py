import threading
import socket
import json
import requests
import datetime
import time
from api import app

clients = []
dispositivosConectados = []
# Lista de mensagens (simulando uma fila de mensagens)
messages = []
lock = threading.Lock()
msg = 'Ligar'
num = 1

enderecos = []

def main():
    try:
        # Inicia os servidores TCP e UDP em threads separadas
        tcp_thread = threading.Thread(target=tcp_udp_server)
        requisicao_thread = threading.Thread(target=requisicao)
        tcp_thread.start()
        requisicao_thread.start()

        # Inicia a aplicação Flask
        app.run(host='0.0.0.0', port=8088, debug=True)

    except Exception as e:
        print('Erro:', e)
        
def tcp_udp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        server.bind(('0.0.0.0', 65432))
        server_udp.bind(("0.0.0.0", 65433))
        server.listen()
    except:
        return print(" * Servidor Funcionando")
    thread3 = threading.Thread(target=receberUdp, args=[server_udp])
    thread3.start()
    while True:
        client, addr = server.accept()
        if addr[0] not in enderecos:
            enderecos.append(addr[0])
            clients.append(client)
        else:
            clients[enderecos.index(addr[0])] = client   
              
def receberUdp(server_udp):
    global dispositivosConectados
    while True:
        try:
            # Recebe dados do cliente UDP
            data_udp, addr_udp = server_udp.recvfrom(1024)
            print('Conectado por UDP:', addr_udp)
            
             # Criar uma nova thread para tratar os dados recebidos
            threading.Thread(target=tratarDados, args=(data_udp, addr_udp)).start()
        except Exception as e:
            print('Item já removido')
            
def tratarDados(data_udp, addr_udp):  
    print('Mensagem recebida do cliente UDP:', data_udp.decode())
    if(data_udp.decode() != "Desligar"):
        if(addr_udp[0] not in dispositivosConectados):
            dispositivosConectados.append(addr_udp[0])
            enviar_para_api(data_udp, addr_udp[0])
        else:
            atualizar_dado_api(data_udp, dispositivosConectados.index(addr_udp[0]) + 1)
    else:
        atualizar_dado_api(data_udp, dispositivosConectados.index(addr_udp[0]) + 1)
        #remover_dispositivo(dispositivosConectados.index(addr_udp) + 1)
        #ispositivosConectados.remove(addr_udp)
            
################################################################################################
#############################    Funções para manipular a API    ###############################
################################################################################################

def pegar_horario_atual_json():
    agora = datetime.datetime.now()
    hora = agora.hour
    minutos = agora.minute
    segundos = agora.second
    
    # Criando um dicionário com os valores
    horario_dict = {
        "hora": hora,
        "minutos": minutos,
        "segundos": segundos
    }
    
    return horario_dict

def enviar_para_api(data_udp, addr):
    url_publish = 'http://127.0.0.1:8088/dispositivos'

    try:
        # Preparar os dados para publicar na API
        payload = {'endereco': addr, 'Dado': data_udp.decode(), 'Data': pegar_horario_atual_json()}  # Supondo que data_udp é uma sequência de bytes
        json_payload = json.dumps(payload)  # Convertendo para JSON
        headers = {'Content-Type': 'application/json'}

        # Publicar na API
        response_publish = requests.post(url_publish, data=json_payload, headers=headers)

        # Verificar se a publicação foi bem-sucedida
        if response_publish.status_code == 201:
            print("Dados UDP enviados com sucesso para a API.")
        else:
            print("Erro ao enviar os dados UDP para a API:", response_publish.status_code)
            return
    except Exception as e:
        print('Erro ao enviar/receber dados para/de API:', e)

def atualizar_dado_api(dado_udp, id):
    url_update = 'http://127.0.0.1:8088/dispositivo/{}'.format(id)

    try:
        # Preparar os dados para atualizar na API
        payload = {'Dado': dado_udp.decode(), 'Data': pegar_horario_atual_json()}
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
        
def remover_dispositivo(dado_id):
    url_delete = 'http://127.0.0.1:8088/dispositivo/{}'.format(dado_id)

    try:
        # Enviar requisição DELETE para remover o dado da API
        response_delete = requests.delete(url_delete)

        # Verificar se a remoção foi bem-sucedida
        if response_delete.status_code == 200:
            print("Dado removido com sucesso da API.")
        else:
            print("Erro ao remover o dado da API:", response_delete.status_code)
            return
    except Exception as e:
        print('Erro ao enviar/receber dados para/de API:', e)

def remover_requisicao(dado_id):
    url_delete = 'http://127.0.0.1:8088/requisicoes/{}'.format(dado_id)

    try:
        # Enviar requisição DELETE para remover o dado da API
        response_delete = requests.delete(url_delete)

        # Verificar se a remoção foi bem-sucedida
        if response_delete.status_code == 200:
            print("Dado removido com sucesso da API.")
        else:
            print("Erro ao remover o dado da API:", response_delete.status_code)
            return
    except Exception as e:
        print('Erro ao enviar/receber dados para/de API:', e)

def requisicao():
    global msg
    global num
    url_consume = 'http://127.0.0.1:8088/requisicoes'  # Rota para consumir a API
    while True:
        try:
            # Consumir a API para obter a mensagem recém-publicada
            response_consume = requests.get(url_consume)
            # Verificar se a mensagem foi consumida com sucesso
            if response_consume.status_code == 200:
                consumed_message = response_consume.json()
                if len(consumed_message) > 0: 
                    print(consumed_message[0])
                    if consumed_message[0]['Dado'] == 'Desligar':
                        msg = 'Desligar'
                        num = consumed_message[0]['Num']
                        print(num, msg)
                    elif consumed_message[0]['Dado'] == 'Ligar':
                        msg = 'Ligar'
                        num = consumed_message[0]['Num']
                        print(num, msg)
                    else:
                        msg = consumed_message[0]['Dado']
                        num = consumed_message[0]['Num']
                    try:
                        print(clients)
                        print((num - 1))
                        clients[(num - 1)].send(msg.encode())
                        remover_requisicao(1)
                    except Exception as e:
                        print(e)
        except Exception as e:
            print('Erro ao enviar/receber dados para/de API:', e)
            pass
        time.sleep(0.5)

################################################################################################
 
if __name__ == "__main__":
    main()