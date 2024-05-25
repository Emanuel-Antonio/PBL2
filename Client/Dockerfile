#Use a imagem Python 3 como base
FROM python:3.9-slim

#Crie o diretório de trabalho na imagem
WORKDIR /app

#Copie o arquivo requirements.txt para a imagem
COPY requirements.txt .
COPY client.py .

#Instale as bibliotecas Python listadas no arquivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# variável de ambiente IP
ENV bank 192.168.1.100

#Comando para iniciar o aplicativo
CMD ["python", "client.py"]