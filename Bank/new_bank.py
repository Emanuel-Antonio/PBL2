from new_api import app
import os

#bank = "172.16.103.14"

#bank = os.getenv("bank")
bank = "192.168.1.105"

def main():

    try:
        # Inicia a aplicação Flask
        app.run(host='0.0.0.0', port=8088, debug=True, threaded=True)

    except Exception as e:
        print('Erro:', e)

if __name__ == "__main__":
    main()