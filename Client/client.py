import requests
import os
import json

IP = os.getenv("IP")
#IP = '172.16.103.8' 
    
def main():
    while True:
        try:
            idDispositivos = []
            statusDispositivos = []
            opcao = int(input("=====================================================\n1 - Ligar\n2 - Desligar\n3 - Mudar Brilho\n4 - Visualizar Dados do Dispositivo\n5 - Visualizar Dispositivos Conectados\n=====================================================\nDigite um comando: ")) 
            print("=====================================================")
            dadoDispositivos = verificaDados()
            for item in dadoDispositivos:
                idDispositivos.append(item['id'])
                statusDispositivos.append(item['Dado']) 
            while opcao < 1 or opcao > 5:
                opcao = int(input("Digite um comando válido: "))
                print("=====================================================")
            if(opcao != 5):   
                num = int(input('Dispositivo: '))
                print("=====================================================")
                while num not in idDispositivos:
                    num = int(input('Digite um Dispositivo válido: '))
                    print("=====================================================")
            while opcao == 3 and statusDispositivos[num-1] == 'Desligado':
                print('Primeiro ligue o dispositivo para alterar o seu Brilho!')
                print("=====================================================")
                opcao = 0
            while opcao == 1 and statusDispositivos[num-1] != 'Desligado':
                print('O dispositivo já está Ligado!')
                print("=====================================================")
                opcao = 0
            while opcao == 2 and statusDispositivos[num-1] == 'Desligado':
                print('O dispositivo já está Desligado!')
                print("=====================================================")
                opcao = 0
            if opcao == 1:
                comando = 'Ligar'
                enviarRequisicao(num, comando)
                print("Ligando dispositivo ...")
                b = input('Digite enter para solicitar outro comando!')
                print("=====================================================")
                while b != '':
                    b = input('Digite enter para solicitar outro comando!\n=====================================================')       
            elif opcao == 2:
                comando = 'Desligar'
                enviarRequisicao(num, comando) 
                print("Desligando dispositivo ...")
                n = input('Digite enter para solicitar outro comando!')
                print("=====================================================")
                while n != '':
                    n = input('Digite enter para solicitar outro comando!\n=====================================================')        
            elif opcao == 3:
                n = int(input("Digite o Brilho: "))
                while n > 100 or n < 0:
                    n = int(input('Digite um valor válido para o Brilho: ')) 
                    print("=====================================================")
                comando = str(n)
                enviarRequisicao(num, comando)   
                print("Mudança efetuada com sucesso ...")
                b = input('Digite enter para solicitar outro comando!') 
                print("=====================================================")
                while b != '':
                    b = input('Digite enter para solicitar outro comando!\n=====================================================') 
            elif opcao == 4:
                for i in range(len(dadoDispositivos)):
                    if i == (num - 1):
                        print("Id: {}\nendereco: {}\nDado: {}\nData: {}".format(dadoDispositivos[i]['id'], dadoDispositivos[i]['endereco'], dadoDispositivos[i]['Dado'], dadoDispositivos[i]['Data']))
                n = input('Digite enter para mandar outra requisição!')
                print("=====================================================")
                while n != '':
                    n = input('Digite enter para solicitar outro comando!\n=====================================================')
            elif opcao == 0:
                n = input('Digite enter para mandar outra requisição!')
                print("=====================================================")
                while n != '':
                    n = input('Digite enter para solicitar outro comando!\n=====================================================')
            else:
                for item in dadoDispositivos:
                    if item != {}:
                        print("Id: {}\nEndereco: {}\nDado: {}\nData: {}\n".format(item['id'], item['endereco'], item['Dado'], item['Data']))
                        print("=====================================================")
                n = input('Digite enter para mandar outra requisição!')
                print("=====================================================")
                while n != '':
                    n = input('Digite enter para solicitar outro comando!\n=====================================================')
        except ValueError as e:
            n = input('Digite enter para mandar outra requisição!')
            print("=====================================================")
            while n != '':
                n = input('Digite enter para solicitar outro comando!\n=====================================================')
        limpar_terminal()
   
def limpar_terminal():
    # Verifica se o sistema operacional é Windows
    if os.name == 'nt':
        os.system('cls')  # Limpa o terminal no Windows
    else:
        # Limpa o terminal em sistemas Unix (Linux, macOS, etc.)
        os.system('clear')   
    
################################################################################################
###################################     API    #################################################
################################################################################################
     
def verificaDados():
    global IP
    url_consume = f'http://{IP}:8088/dispositivos'  # Rota para consumir a API
    consumed_message = {}
    try:
        # Consumir a API para obter a mensagem recém-publicada
        response_consume = requests.get(url_consume, timeout=2)

        # Verificar se a mensagem foi consumida com sucesso
        if response_consume.status_code == 200:
            consumed_message = response_consume.json()
        else:
            print("Erro ao consumir a API:", response_consume.status_code)
    except Exception as e:
        print('Não foi possível estabelecer uma conxão com o Broker ...')
    return consumed_message

def enviarRequisicao(num, comando):
    global IP
    url_publish = f'http://{IP}:8088/requisicoes'

    try:
        # Preparar os dados para publicar na API
        payload = {'Dado': comando, 'Num': num}  # Supondo que data_udp é uma sequência de bytes
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
                   
if __name__=="__main__":
    main()