
<div align="center">

# PBL2-Redes - Sistema de Bancos Distribuídos

</div>

<A name= "Intr"></A>

# Introdução

Nos últimos anos, a adoção de movimentações financeiras exclusivamente por dispositivos móveis cresceu significativamente, impulsionada pela criação do Pix e pelo forte investimento dos bancos em aplicativos. Tal movimento transformou a maneira como os brasileiros realizam pagamentos, permitindo a inclusão financeira de milhões de pessoas. Inspirados pelo sucesso do Pix, o governo de um país sem banco central deseja desenvolver um sistema semelhante que permita a criação de contas bancárias, facilitando pagamentos, depósitos e transferências entre diferentes bancos sem a necessidade de um controle centralizado. Para isso, foi formado um consórcio bancário para desenvolver uma solução robusta e segura utilizando Python. Esta solução, através de um conjunto de estratégias, garante que as transações sejam atômicas e previne problemas como o duplo gasto, oferecendo uma infraestrutura confiável e eficiente para os clientes de todos os bancos participantes.

# Sumário
- <A href = "#Intr">Introdução</A><br>
- <A href = "#Brok">Broker</A><br>
- <A href = "#Dispositivo">Dispositivo</A><br>
- <A href = "#Cliente">Cliente</A><br>
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

<A name= "Brok"></A>
# Broker

Em geral o componente Broker serve de intermediador entre os "Clientes" e os "Dispositivos" e lida tanto com as comunicações TCP/IP e HTTP através da API.

## Arquivo Auxiliar (api.py)

Este arquivo consiste na criação das rotas para que possamos importar e executar a API no arquivo broker.py. Isto foi feito para que o arquivo broker.py não fique poluído. Ademais, vale falar que nele utilizamos rotas POST, GET, PUT e DELETE.

## Arquivo Principal (broker.py)

Agora uma breve explicação sobre cada uma das funções do broker.py.

  - ***main():*** Responsável por criar duas threads, tcp_thread e requisicao_thread, as quais executam as funções tcp_udp_server e requisicao, respectivamente. Entretanto, após isto ele ainda inicia a aplicação Flask.

  - ***tcp_udp_server():*** Aqui é feito a criação dos sockets UDP e TCP, além de deixar ele escutando conexões TCP, para guardar tais conexões em um lista de conexões para uso futuro. Ademais, a criação da thread que irá escutar mensagens UDP também é feita nessa função.  

  - ***receberUdp():*** Está função por sua vez faz somente a recepção dos dados UDP e repassa para ser tratado em uma thread que roda a função tratar dados.

  - ***tratarDados(data_udp, addr_udp):*** Tal função se compromete a fazer o tratamento adequado do dado UDP recebido. Ele pode utilizar os métodos POST e PUT através de rotas especificas para armazenar esses dados em um arquivo json. 

  - ***pegar_horario_atual_json():*** Essa outra função está responsável somente por pegar o horário atual e guardar a hora, minuto e segundo em um dicionário.

  - ***enviar_para_api(data_udp, addr):*** Função como o nome já diz envia os dados UDP recebidos para a API através de rotas, tais dados formam um dispositivo.

  - ***atualizar_dado_api(dado_udp, id):*** Simplesmente, esta função usa rotas da API para atualizar informações em vez de criar novos dispositivos.

  - ***remover_dispositivo(dado_id):*** Como o nome já fala, essa função se responsabiliza por remover dispositivos da API através de rotas.

  - ***remover_requisicao(dado_id):*** Esta outra função se responsabiliza por remover dados da API, contudo, diferente da última função ele remove requisições e não dispositivos.

  - ***requisicao():*** Por fim, essa última função trabalha em thread para que ele possa rebecer constantemente requisições e repassar essas requisições para os respectivos dispositivos.
    
<A name= "Dispositivo"></A>
# Dispositivo

O dispositivo serve para simular um componente IoT. Neste projeto, ele é uma lâmpada que pode ser ligada, desligada ou ter seu brilho alterado remotamente.

## Arquivo Principal (dispositivo.py)

- ***main():*** Essa função é responsável por criar os sockets, iniciar uma comunicação TCP com o broker e criar três threads, que são threads das funções receberTcp, enviarDadoUdp e menu, respectivamente.
  
- ***menu():*** Essa função tem como propósito mostrar o menu de opções e esperar uma entrada do usuário.
  
- ***receberTcp(client):*** Essa função como o nome diz está responsável por aguardar mensagens do Broker e fazer alterações em variáveis quando preciso. Note também que ele recebe um argumento client, o qual guarda a conexão que ele deverá escutar.
    
- ***enviarDadoUdp(client_udp):*** Esta função como o nome fala, tem como responsabilidade enviar os dados continuamente para o Broker. Observe que ele possui um argumento client_udp, este guarda uma conexão assim como a função anterior, contudo essa conexão é UDP ao invés de TCP.

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
