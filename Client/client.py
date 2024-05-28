class Client:
    def __init__(self, nome, idade, password, id, saldo=0.0):
        self._nome = nome
        self._idade = idade
        self._password = password
        self._id = id
        self._saldo = saldo

    # Getter e Setter para nome
    @property
    def nome(self):
        return self._nome
    
    @nome.setter
    def nome(self, value):
        self._nome = value

    # Getter e Setter para idade
    @property
    def idade(self):
        return self._idade
    
    @idade.setter
    def idade(self, value):
        self._idade = value

    # Getter e Setter para password
    @property
    def password(self):
        return self._password
    
    @password.setter
    def password(self, value):
        self._password = value

    # Getter e Setter para id
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value

    # Getter e Setter para saldo
    @property
    def saldo(self):
        return self._saldo
    
    @saldo.setter
    def saldo(self, value):
        if value >= 0:
            self._saldo = value
        else:
            print('O saldo não pode ser negativo.')

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
