from client import *
import os
import requests

bank = os.getenv("bank")

def login(users):
    print("------------------------------")
    print(" 1 - Entrar\n 2 - Criar conta\n ")
    opcao = int(input("===>"))
    print("------------------------------")
    while opcao < 1 or opcao > 2:
        print("Escreva uma opção válida!\n")
        opcao = int(input("==>"))
        print("------------------------------")
    if opcao == 1:
        cod = int(input("Digite o código da conta\n==>\n"))
        password = input("Digite a senha\n==>\n")
        for user in users:
            if (cod == user['id']) and (password == user['password']):
                print("Login efetuado com sucesso")
        else:
            print("Usuário ou senha inválido!\n Tente acessar uma conta existente ou crie uma conta")
                
    else:
        pass
        
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
     
def main():
    users = []
    users = getUsers()
    while True:
        login(users)
    
        
if __name__=="__main__":
    main()
    

    
    
