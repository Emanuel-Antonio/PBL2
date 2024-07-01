
<div align="center">

# PBL2-Redes - Sistema de Bancos Distribuídos

</div>

<A name= "Intr"></A>

# Introdução
<p align='justify'>
Nos últimos anos, a adoção de movimentações financeiras exclusivamente por dispositivos móveis cresceu significativamente, impulsionada pela criação do Pix e pelo forte investimento dos bancos em aplicativos. Tal movimento transformou a maneira como os brasileiros realizam pagamentos, permitindo a inclusão financeira de milhões de pessoas. Inspirados pelo sucesso do Pix, o governo de um país sem banco central deseja desenvolver um sistema semelhante que permita a criação de contas bancárias, facilitando pagamentos, depósitos e transferências entre diferentes bancos sem a necessidade de um controle centralizado. Para isso, foi formado um consórcio bancário para desenvolver uma solução robusta e segura utilizando Python. Esta solução, através de um conjunto de estratégias, garante que as transações sejam atômicas e previne problemas como o duplo gasto, oferecendo uma infraestrutura confiável e eficiente para os clientes de todos os bancos participantes.
</p>

# Sumário
- <A href = "#Intr">Introdução</A><br>
- <A href = "#Api">Api</A><br>
- <A href = "#Interface">Interface Cli</A><br>
- <A href = "#Arq">Arquitetura da solução</A><br>
- <A href = "#Apli">Protocolo de comunicação entre dispositivo e Broker - camada de aplicação</A><br>
- <A href = "#Tran">Protocolo de comunicação entre dispositivo e Broker - camada de transporte</A><br>
- <A href = "#Rest">Interface da Aplicação </A><br>
- <A href = "#Form">Formatacao, envio e tratamento de dados</A><br>
- <A href = "#Trat">Tratamento de conexões simultaneas </A><br>
- <A href = "#Geren">Gerenciamento do dispositivo</A><br>
- <A href = "#Desem">Desempenho </A><br>
- <A href = "#Conf">Confiabilidade da solução </A><br>
- <A href = "#Exec">Como Executar</A><br>
- <A href = "#clie">Interface do Cliente</A><br>
- <A href = "#Disp">Interface do Dispositivo</A><br>
- <A href = "#Conc">Conclusão</A><br>

<A name= "Api"></A>
# Api

<p align='justify'>
A API atua como servidor para um banco específico, permitindo aos usuários acessar diversas funcionalidades, tais como: criação de contas, realização de transferências, depósitos, saques, entre outras. Toda a comunicação ocorre por meio de uma API REST, implementada com Flask, uma biblioteca versátil da linguagem Python.
</p>

## Arquivo Principal (new_api.py)

<p align='justify'>
Este arquivo contém as rotas responsáveis pela gerenciamento de transações via token e pela realização de transações bancárias. Ele implementa métodos HTTP POST, GET, PUT e DELETE para operações específicas. Abaixo estão detalhadas as funcionalidades de cada rota e função desse arquivo.
</p>

 `Observação:` Vale ressaltar que a dinâmica de utilização do token para o gerenciamento de transações será abordada na subseção "Rede em Anel" da seção "Concorrência".
 
### Rotas

  - ***/id:*** Rota GET responsável por fornecer um ID válido para uso em um pacote de transações. Retorna o ID e o código 201 quando bem-sucedido.

   - ***/status:*** Rota GET responsável por verificar o status de um pacote de transações enviado para execução no banco, utilizando o ID da transação recebido no JSON, retorna o código 201 se o pacote foi executado com sucesso e 401 caso contrário.

   - ***/receive_token:*** Rota POST responsável por receber o token de outro banco do consórcio. Retorna o código 200 quando o token é recebido com uma sequência válida. A sequência estará presente no JSON.

   - ***/login:*** Rota POST responsável por verificar o usuário e senha enviados pelo JSON. Retorna o código 201 quando as credenciais correspondem aos dados do banco; caso contrário, retorna 401.

   - ***/users:*** Rota GET responsável por pegar os dados de todos os usuários do banco. Retorna 201 quando executado adequandamente. Vale informar que por segurança nenhum retorno da API retorna dados de senha.

   - ***/users/user_id:*** Rota GET responsável por pegar os dados de um usuário específico, através do user_id. Retorna 201 quando executado adequandamente e 401 caso contrário.

   - ***/users:*** Rota POST responsável por criar um usuário no banco. Retorna 201 quando executado adequandamente.

   - ***/users/user_id/accounts:*** Rota POST responsável por postar uma nova conta a um usuário existente, através do parametro user_id. Retorna 201 quando executado adequandamente e 401 caso contrário.

   - ***/users/user_id/accounts:*** Rota GET responsável por pegar todas as contas de um usuário específico, através do user_id. Retorna 201 quando executado adequandamente e 401 caso contrário.

   - ***/users/user_id/accounts/account_id:*** Rota GET responsável por pegar uma conta específico, através do user_id e account_id. Retorna 201 quando executado adequandamente e 401 caso contário.

   - ***/users/user_id:*** Rota DELETE responsável por deletar um usuário específico, através do user_id. Retorna 201 quando executado adequandamente.

   - ***/users/user_id:*** Rota PUT responsável por atualizar um usuário específico, através do user_id. Seu retorno é 201 para atualizado com sucesso e 401 caso contrário.

   - ***/users/user_id/accounts/account_id/deposit:*** Rota responsável por realizar um deposito em uma conta especificada pelo user_id e account_id. O JSON só indica o valor a ser depositado. Como as outras rotas, o retorno 201 representa que a operação foi bem sucedida e 401 representa o oposto.

   - ***/users/user_id/accounts/account_id/take:*** Rota responsável por realizar um saque em uma conta especificada pelo user_id e account_id. O JSON indica apenas o valor do saque. Assim como nas outras rotas, retorna o código 201 quando executado adequadamente e 401 caso contrário.

   - ***/sender:*** Rota responsável por adicionar o valor transferido à conta de destino, utilizando o ID e o valor recebidos do JSON. Ademais, retorna o código 201 se a operação for bem-sucedida e 401 caso contrário.

   - ***/abort:*** Rota responsável por reverter uma transação de um pacote. Ela utiliza do ID e valor recebido para realizar essa operação e retorna o código 201 se a reversão for bem-sucedida e 401 caso contrário.

   - ***/recipient:*** Rota responsável por receber um valor e um ID, e realizar o débito desse valor no saldo da conta associada a esse ID. Vale ressaltar que seu retorno é 201 quando executada corretamente e 401 caso contrário.

   - ***/transfers:*** Rota responsável por receber pacotes de transações da interface CLI a qualquer momento e armazená-los na lista de transferências. Se executada adequadamente, retorna o código 201; caso contrário, retorna 401.
     
### Funções

  - ***pass_token():*** Esta função opera em uma thread no servidor e tem como propósito transferir o token para outro banco dentro do consórcio. A transferência ocorre somente quando todas as condições necessárias para o repasse do token são satisfeitas.

  - ***receive_token():*** Esta função é responsável por executar uma sequência de operações imediatamente após receber o token pela rota designada. Primeiro, ela tenta realizar a operação. Em seguida, ela atualiza o valor de uma variável global, liberando uma thread encarregada de passar o token para outro banco do consórcio.

  - ***check_token():*** Esta função verifica o tempo que o banco está sem o token. Ademais, ela opera em uma thread separada para não interferir nas outras funções do servidor do banco e caso o banco fique sem o token por um período específico, a função interpreta que o consórcio perdeu o token e regenera um novo.

  - ***find_account(user, account_id):*** Esta função é responsável por buscar uma conta específica utilizando os parâmetros user e account_id. Retorna None caso a conta não exista no banco.

  - ***find_user(user_id):*** Função responsável por buscar um usuário específico na lista de usuários, utilizando o parâmetro user_id. Retorna None caso o usuário não seja encontrado.
  
  - ***abort_transactions(transactions):*** Esta função desempenha um papel crucial na garantia da atomicidade, sendo responsável por reverter as transações do pacote em caso de problemas durante sua execução. A rota "/abort" é utilizada para desfazer as transações que foram realizadas com sucesso anteriormente, e que estavam no mesmo pacote da transação que falhou.
    
  - ***transfer(transations):*** Tal função se caracteriza por executar todas as transações recebidas de maneira segura, garantindo a atomicidade dentro do pacote de transações passado como parâmetro desta função. Ademais, ao finalizar retorna True quando o pacote é executado com sucesso e False caso contrário.
 
  - ***init_server_flask():*** Esta função é responsável por inicializar a aplicação Flask.

  - ***main():*** Por último, esta função, como o próprio nome indica, é responsável pela ordem de execução das outras funções e rotas. Neste arquivo, ela é concisa, focando na inicialização das threads para passagem de token, verificação de token e da API do banco.
    
<A name= "Interface"></A>
# Interface Cli

O dispositivo serve para simular um componente IoT. Neste projeto, ele é uma lâmpada que pode ser ligada, desligada ou ter seu brilho alterado remotamente.

## Arquivo Principal (new_user.py)

- ***limpar_terminal():*** Esta função tem como responsabilidade limpar o terminal. Para isso, ela verifica o sistema operacional para determinar qual função utilizar. Isto pois para limpar o terminal no "Windows" é diferente de limpar no "Linux".

   `Observação:` Vale ressaltar que boa parte dessas funções possuem um bloco try-catch, visto que realizam operações delicadas. Mais detalhes podem ser encontrados na documentação do código.
  
<A name= "Cliente"></A>
# Cliente

O cliente serve para simular uma interface de controle remoto, a qual pode enviar comandos para vários dispositivos com o auxílio do Broker. Observe que essa interface é uma interface de linha de comando (CLI) e não gráfica.

## Arquivo Principal (cliente.py)

- ***main():*** Essa função será responsável pela execução geral do código, incluindo a exibição do menu, a espera de entradas e o encaminhamento de requisições e solicitações para outras funções.

- ***enviarRequisicao(num, comando):*** Esta outra função, como o próprio nome indica, realiza o envio de requisições para a API, utilizando o método POST. Além disso, ela recebe os argumentos num e comando, que representam o identificador (ID) do dispositivo e o comando a ser enviado, respectivamente.

- ***verificaDados():*** Esta função tem como responsabilidade utilizar o método GET para adquirir os dados dos dispositivos, através da API.

- ***limpar_terminal():*** Esta função tem como responsabilidade limpar o terminal. Para isso, ela verifica o sistema operacional para determinar qual função utilizar. Isto pois para limpar o terminal no "Windows" é diferente de limpar no "Linux".

  `Observação:` Vale ressaltar que boa parte dessas funções também possuem um bloco try-catch, visto que realizam operações delicadas. Mais detalhes podem ser encontrados na documentação do código.

# Tecnologias utilizadas

- ***Ferramantas:*** Para o desenvolvimento desta aplicação, utilizamos ferramentas como Insomnia e Visual Studio Code.

- ***Outras:*** Para a produção do código fonte, utilizamos a linguagem de programação Python, além de algumas bibliotecas dessa linguagem, tais como requests, Flask, etc.

<A name="Arq"></A>
# Arquitetura da solução

Sobre a arquitetura utilizada para a troca de mensagens podemos citar a conexão "Dispositivo <-> Broker" e "Broker <-> Cliente". Além disso, utilizamos três componentes, sendo eles: dispositivo, broker e cliente. Note que ambos os componentes possuem uma seção contendo mais detalhes.
  
- ***Dispositivo -> Broker:*** A comunicação entre os dispositivos e o broker para o envio de dados foi feita através de sockets, via protocolo TCP/IP. Neste caso, utilizamos o protocolo UDP, pois ao enviarmos dados, a velocidade de envio foi uma prioridade.

     `Observação:` Note que a conexão TCP é inicializada pelo dispositivo, permitindo que o broker envie requisições para os dispositivos conectados sem a necessidade de abrir múltiplas conexões pelo broker, o que demandaria a busca por diversos endereços físicos. No entanto, ele não envia dados utilizando TCP.
  
- ***Broker -> Dispositivo:*** A comunicação entre o broker e os dispositivos para o envio de comandos/requisições foi feita, assim como a comunicação do dispositivo com o broker, usando sockets, via protocolo TCP/IP. Porém, ao contrário da comunicação de dados, utilizamos o TCP, a fim de priorizar a segurança do envio de requisições.
   
- ***Broker <-> Cliente:*** A comunicação entre o broker e o cliente foi realizada por meio de rotas de uma API REST, utilizando verbos como: GET, POST, PUT E DELETE.

  `Definição:` Uma API REST (Representational State Transfer) é uma arquitetura de comunicação que utiliza os princípios do protocolo HTTP para permitir a comunicação entre sistemas distribuídos.

Ademais, ainda precisamos falar sobre a ordem que essas comunicações acontecem, para isso observe a <br/> <em>Figura 1.</em> <br/>

 <div align="center">
   
   ![Figura 1](Imagens/Diagrama.png)
   <br/> <em>Figura 1. Camada de Transporte.</em> <br/>
   
   </div>

Analisando a imagem, mais especificamente na parte "Envio de comandos", fica evidente que todas as informações passam pelo broker, independentemente de serem dados ou comandos. Por exemplo, se desejo enviar uma mensagem remotamente do cliente para um dispositivo, devo adicionar o comando à minha API através de uma rota. Em seguida, o broker utilizará o protocolo TCP/IP para enviar o comando ao dispositivo via TCP. Já na parte "Conexão Dispositivo -> Broker", é nos mostrado que o dispositivo inicia a comunicação TCP, a fim de que o broker identifique e armazene as conexões.
   
# Protocolo de Comunicação entre Dispositivo e Broker

 <A name="Apli"></A>
- ***Camada de Aplicação:***

   - **Dispositivo:** Sobre o protocolo que o dispositivo utiliza para se comunicar com o broker, devemos abordar que o dispositivo começa criando uma comunicação TCP. Isto apenas para armazenar a conexão no broker. A partir desse ponto, ele cria a comunicação UDP e envia os dados continuamente a cada meio segundo para o broker.
     
       `Observação:` É válido mencionar que os dados enviados via UDP consistem em um dado, seguida pelo endereço IP do dispositivo e a porta que ele utilizou para a comunicação. Além disso, esse dado pode representar o estado de 'Desligado' ou, respectivamente, o brilho atual do dispositivo. Note que para identificar se o dispositivo está ligado basta verificar se o dado é diferente de 'Desligado'.
     
   - **Broker:** Por parte do dispositivo, ele só encaminha mensagens utilizando TCP quando necessário. Para isso, ele verifica se há alguma requisição na API. Se for o caso, ele envia o dado para o respectivo dispositivo através da conexão previamente estabelecida. Esses dados podem ser "Desligar", "Ligar" ou o brilho a ser alterado. Por outro lado, na parte da aplicação, a cada dado que chega, é verificado se o dispositivo já foi armazenado. Se não foi, todos os dados são enviados para a API, incluindo Dado, Id, Endereço e Data. Caso contrário, apenas o Dado é atualizado na API.

  - **Cliente:** O cliente envia os dados para a API quando solicitado. Nesse caso, ele fará uma requisição POST em uma determinada rota, que receberá os dados IP, Num e Dado, respectivamente. Além disso, quando for solicitado um dado de um dispositivo, o cliente apenas fará a leitura dos dados através de outra rota existente.
    
     `Observação:` Os dados do IP são preenchidos automaticamente pela API. Já o número do dispositivo será escolhido pelo usuário e o Dado pode ser "Desligar", "Ligar" ou um inteiro referente ao valor do brilho a ser alterado.
  
<A name="Tran"></A>
- ***Camada de Transporte:***

   - **Dispositivo:** Sobre o protocolo utilizado pelo dispositivo para se comunicar com o broker, é importante mencionar que foi utilizado o protocolo UDP para o envio de dados. A razão para optar pelo UDP em vez do TCP nesse caso é que o User Datagram Protocol (UDP) é caracterizado por uma baixa sobrecarga, uma vez que não incorpora mecanismos de controle de fluxo, retransmissão de pacotes ou garantias de entrega ordenada. Isso o torna mais eficiente em termos de largura de banda e tempo de latência. Além disso, sua natureza sem conexão e sem garantias proporciona uma baixa latência em comparação com o Transmission Control Protocol (TCP), tornando-o ideal para aplicativos que demandam uma resposta rápida e em tempo real, como streaming de áudio e vídeo, bem como jogos online. Em suma, mesmo que ocorra perda de dados, a velocidade de transmissão ainda compensa na maioria dos casos.
     
   - **Broker:** Falando do Broker, ele se comunica com o dispositivo utilizando o protocolo TCP para o envio de comandos. Porque, o Transmission Control Protocol (TCP) oferece confiabilidade ao garantir a entrega, ordem e integridade dos dados, utilizando mecanismos como confirmações de recebimento e retransmissões de pacotes perdidos. Além disso, o TCP inclui algoritmos para controlar o fluxo de dados entre remetente e destinatário, evitando sobrecarga do destinatário, e mecanismos para detectar e reagir a congestionamentos na rede, ajustando dinamicamente a taxa de transmissão. Outro aspecto importante é a garantia de entrega ordenada dos dados, fundamental para aplicativos que exigem essa ordem, como transferências de arquivos e streaming de mídia. Em resumo, utilizamos o TCP porque não queremos perder comandos/requisições.

<A name="Rest"></A>
# Interface da Aplicação (REST)

Em relação a API foram criadas 8 rotas, as quais utilizaram verbos/métodos como POST, PUT, GET e DELETE.

- ***POST:*** Em relação aos métodos POST, temos duas rotas que à utilizam, sendo que um posta dispositivos em minha aplicação e a outra posta requisições, a rota da primeira do dispositivo é "http://{id do broker}//dispositivos" e a rota da requisição é "http://{id do broker}//requisicoes". Podemos ver a estrutura para construção dessas rotas na Figura 2.
  
  <div align="center">
   
   ![Figura 2](Imagens/POST.png)
   <br/> <em>Figura 2. Métodos POST.</em> <br/>
   
   </div>

- ***PUT:*** Só há uma rota que utiliza o este método, tal rota se chama "http://{id do broker}//dispositivo/{id do dispositivo}". Vale lembrar que essa método realiza atualizações na minha API. Mais detalhes na Figura 3.

<div align="center">
   
   ![Figura 3](Imagens/PUT.png)
   <br/> <em>Figura 3. Método PUT.</em> <br/>
   
   </div>

- ***GET:*** Já em relação aos métodos GET utilizados, temos 3, os quais são dois para dispositivos e um para requisições. As do dispositivo são as rotas "http://{id do broker}//dispositivos/{id do dispositivo}" para acessar os dados de um único dispositivo e "http://{id do broker}//dispositivos" para acessar os dados de todos os dispositivos. A rota de requisições é "http://{id do broker}//requisicoes". Podemos ver mais detalhes na Figura 4.

<div align="center">
   
   ![Figura 4](Imagens/GET.png)
   <br/> <em>Figura 4. Métodos GET.</em> <br/>
   
   </div>

- ***DELETE:*** Por fim os métodos DELETE, temos 2, assim como os métodos POST, sendo um para dispositivos e outro para requisições, cujas rotas são "http://{id do broker}//dispositivo/{id do dispositivo}" e "http://{id do broker}//requisicoes/{id da requisição}". Para mais detalhes observe a Figura 5.

<div align="center">
   
   ![Figura 5](Imagens/DELETE.png)
   <br/> <em>Figura 5. Métodos DELETE.</em> <br/>
   
   </div>
<A name="Form"></A>
# Formatação, Envio e Tratamento de Dados

A formatação dos dados já foi mencionada anteriormente, reforçando elas são enviadas como strings específicas enviadas em bytes por partes do dispositivo para o broker e vice-versa. Já o broker envia para o cliente através da API que entende o formato JSON. Em relação ao envio para a API, ele utiliza rotas para fazer POST, DELETE, PUT e GET, e na parte dos sockets, ele usa a função sendto. Vale lembrar que, se não enviarmos no formato correto, haverá erros. Para evitar isso, sempre convertemos em bytes para enviar usando sockets e em JSON para enviar para a API. Na Figura 6, podemos ver sobre o formato do JSON dos dispositivos e na Figura 7, podemos ver o formato do JSON das requisições.

<div align="center">
   
   ![Figura 6](Imagens/Dispositivo.png)
   <br/> <em>Figura 6. Formato json dos Dispositivos.</em> <br/>
   
   </div>

<div align="center">
   
   ![Figura 7](Imagens/Requisicao.png)
   <br/> <em>Figura 7. Formato json das Requisições.</em> <br/>
   
   </div>
   
<A name="Trat"></A>
# Tratamento de Conexões Simultâneas

Sobre o tratamento de múltiplas conexões, utilizamos threads tanto para receber dados, enviar dados e aceitar entrada de dados do terminal, tudo de maneira paralela. Em relação aos problemas de conectividade, não foram identificados, já que esses problemas ocorrem quando há uma extrema quantidade de dispositivos e clientes, e pela quantidade de aparelhos conectados na aplicação não houve esse tipo de problema. Contudo, vale falar sobre os possíveis problemas ao utilizarmos threads, sendo eles: Condições de corrida, Deadlocks, Starvation, Overhead e Dificuldade de depuração.

`Definições:` 

- **Condições de corrida:** Quando várias threads tentam acessar e modificar os mesmos dados ao mesmo tempo, podem ocorrer resultados inconsistentes.

- **Deadlocks:** Ocorre quando duas ou mais threads ficam aguardando indefinidamente por recursos que a outra possui. Isso pode paralisar o sistema.

- **Starvation:** Algumas threads podem ficar impedidas de fazer progresso devido a outras threads monopolizarem recursos necessários.

- **Overhead:** O uso excessivo de threads pode levar a um alto consumo de recursos do sistema, como memória e CPU, devido ao contexto de comutação e à sincronização necessária entre as threads.

- **Dificuldades de depuração:** Problemas de concorrência podem ser difíceis de reproduzir e depurar, especialmente em sistemas complexos com muitas threads em execução simultânea.

`Observação:` Pelo uso que foi feito dessa aplicação não foi preciso se preocupar com essas questões, contudo para a ampliação de dispositivos e clientes seria de suma importância relevarmos todos os possivéis problemas.  

<A name="Geren"></A>
# Gerenciamento do Dispositivo

No gerenciamento dos dispositivos, podemos ligá-los, desligá-los e ajustar o brilho, tanto diretamente no arquivo dispositivo.py quanto remotamente no arquivo cliente.py.

<A name="Desem"></A>
# Desempenho

Sobre o desempenho, exploramos algumas estratégias, como usar threads para receber e enviar dados UDP e TCP. Também usamos threads para lidar com as solicitações HTTP dos clientes. Além disso, na parte das solicitações, destacamos o uso de filas para priorizar aquelas que chegaram primeiro. Essas estratégias ajudam a garantir eficiência e bom desempenho. Essa fila pode ser identificada na função "requisicao()" do arquivo broker.py, já as threads se encontram tanto no arquivo broker.py como no dispositivo.py.

<A name="Conf"></A>
# Confiabilidade da Solução

Quanto à confiabilidade da solução, ou seja, à segurança das conexões quando o acesso à Internet de um dos componentes é excluído, observa-se que o sistema continua funcionando. Isso ocorre porque há tratamento para exceções geradas ao tentar enviar dados para a API ou ao consumir, por meio do cliente, assim como ao tentar enviar dados via TCP/IP pelo dispositivo. Além disso, o broker não enfrenta esse tipo de problema, pois pode receber conexões de múltiplos dispositivos e clientes, além de substituir as conexões realizadas pela mesma maquina.

<A name="Exec"></A>
# Como Executar

## Etapas:

### 1. Configuração do Ambiente:

   - **Requisitos do Sistema:** Será preciso ter ao menos o Docker instalado na máquina para que seja possível criar a imagem e executá-la.
     
### 2. Obtenção do Código Fonte:

   - **Clonagem do Repositório:** Você pode utilizar o seguinte comando no terminal para adquirir a aplicação:                                          

           git clone https://github.com/Emanuel-Antonio/PBL-Redes.git.
     
   - **Download do Código Fonte:** Caso não tenha o Git na máquina, você pode fazer o download desse repositório manualmente. Vá até o canto superior, selecione "Code" e depois "Download ZIP", e então extraia o arquivo ZIP na sua máquina.

### 3. Configuração da Aplicação:

   - **Arquivos de Configuração:** Abra as pastas "Cliente" e "Dispositivo" e altere nos arquivos "cliente.py" e "dispositivo.py" o endereço IP para o endereço da máquina onde o broker esteja rodando.

### 4. Execução da Aplicação:

   - **Com Docker:**
     
     1. Execute o seguinte comando no terminal dentro das pastas Cliente, Dispositivo e Broker: "docker build -t nome_do_arquivo .", para gerar as imagens, repita três vezes.
        
     2. Agora execute as imagens usando o comando "docker run --network='host' -it -e IP=ipBroker nome_da_imagem" para executar as imagens do dispositivo e do cliente, já para executar a imagem do broker use "docker run --network='host' -it nome_da_imagem".

<A name="clie"></A>
# Interface do Cliente

Observe que abaixo seguem algumas Figuras que mostram como a interface CLI se comporta. Vale informar que a entrada está devidamente validada. Observe que a interface do Cliente é o atuador remoto dos Dispositivos e, assim como já mencionado, trabalha em conjunto com o Broker.

<div align="center">
   
   ![Figura 8](Imagens/menucliente.png)
   <br/> <em>Figura 8. Menu Cliente.</em> <br/>
   
   </div>

  <div align="center">
   
   ![Figura 9](Imagens/opcao2cliente.png)
   <br/> <em>Figura 9. Desligando o Dispositivo.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 10](Imagens/opcao5cliente1.png)
   <br/> <em>Figura 10. Opção 5 para visualizar os Dispositivos Conectados e suas informações.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 11](Imagens/opcao1cliente.png)
   <br/> <em>Figura 11. Ligando o Dispositivo.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 12](Imagens/opcao5cliente.png)
   <br/> <em>Figura 12. Opção 5 para visualizar os Dispositivos Conectados e suas informações.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 13](Imagens/opcao4cliente.png)
   <br/> <em>Figura 13. Opção 4 para visualizar os dados de um Dispositivo específico.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 14](Imagens/opcao3cliente.png)
   <br/> <em>Figura 14. Mudando o Brilho de certo Dispositivo.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 15](Imagens/opcao5cliente2.png)
   <br/> <em>Figura 15. Opção 5 para visualizar os Dispositivos Conectados e suas informações.</em> <br/>
   
   </div>

  `Observação:` Note que a essas imagens também demonstram alguns testes no meu arquivo "cliente.py".

<A name="Disp"></A>
# Interface do Dispositivo

Sobre a interface do Dispositivo, podemos verificar como ela se comporta de acordo com as Figuras a seguir. Além disso, assim como a interface do cliente, também está devidamente validada.

<div align="center">
   
   ![Figura 16](Imagens/opcao2dispositivo.png)
   <br/> <em>Figura 16. Desligando o Dispositivo.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 17](Imagens/opcao4dispositivo.png)
   <br/> <em>Figura 17. Opção 4 para visualizad as informações do Dispositivo.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 18](Imagens/opcao1dispositivo.png)
   <br/> <em>Figura 18. Ligando o Dispositivo.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 19](Imagens/opcao4dispositivo1.png)
   <br/> <em>Figura 19. Opção 4 para visualizar as informações do Dispositivo.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 20](Imagens/opcao3dispositivo.png)
   <br/> <em>Figura 20. Mudando o Brilho do Dispositivo.</em> <br/>
   
   </div>

   <div align="center">
   
   ![Figura 21](Imagens/opcao4dispositivo2.png)
   <br/> <em>Figura 21. Opção 4 para visualizar as informações do Dispositivo.</em> <br/>
   
   </div>

   `Observação:` Note que a essas imagens também demonstram alguns testes no meu arquivo "dispositivo.py".
   
<A name="Conc"></A>
# Conclusão

Enfim, destaco que este projeto atende a todas as exigências previamente propostas e desempenha um papel significativo no aprimoramento das habilidades na área de concorrência e conectividade.
