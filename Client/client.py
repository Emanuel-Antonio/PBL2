class Client:
    def __init__(self, nome, idade, password, id, saldo=0.0):
        self.nome = nome
        self.idade = idade
        self.password = password
        self.saldo = saldo
        self.id = id

    def depositar(self, quantia):
        if quantia > 0:
            self.saldo += quantia
            print(f'Depositado: R${quantia:.2f}. Saldo atual: R${self.saldo:.2f}')
        else:
            print('A quantia de depósito deve ser positiva.')

    def sacar(self, quantia):
        if 0 < quantia <= self.saldo:
            self.saldo -= quantia
            print(f'Sacado: R${quantia:.2f}. Saldo atual: R${self.saldo:.2f}')
        elif quantia > self.saldo:
            print('Saldo insuficiente.')
        else:
            print('A quantia de saque deve ser positiva.')

    def exibir_informacoes(self):
        print(f'Nome: {self.nome}')
        print(f'Idade: {self.idade}')
        print(f'Saldo: R${self.saldo:.2f}')
