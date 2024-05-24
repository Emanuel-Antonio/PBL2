#Use a imagem Python 3 como base
FROM python:3.9-slim

#Crie o diretório de trabalho na imagem
WORKDIR /app

#Copie o arquivo requirements.txt para a imagem
COPY requirements.txt .
COPY bank.py .
COPY api.py .

#Instale as bibliotecas Python listadas no arquivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#Comando para iniciar o aplicativo
CMD ["python", "bank.py"]