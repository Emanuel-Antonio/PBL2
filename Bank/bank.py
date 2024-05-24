from api import app

clients = []

enderecos = []

def main():
    try:
        # Inicia a aplicação Flask
        app.run(host='0.0.0.0', port=8088, debug=True)

    except Exception as e:
        print('Erro:', e)
         
if __name__ == "__main__":
    main()