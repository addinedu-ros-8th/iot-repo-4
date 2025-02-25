from flask import Flask, request, jsonify
import serial
import requests

HOST = '192.168.0.11'
PORT = 80

app = Flask(__name__)

@app.route('/send', methods=['POST'])
def receive_data():
    data = request.get_json()
    
    response = {"message": "Data received"}

    if data['io'] == "led":
        msg = "LED ON" if data['value'] == 1 else "LED OFF"
        position = "LO" if data['value'] == 1 else "LF"
        url = f"http://{HOST}:{PORT}/{position}"
        requests.get(url)
        response = {"message": "Data received", "received": msg}

    elif data['io'] == "garage":
        msg = "garage open" if data['value'] == 1 else "garage close"
        response = {"message": "Data received", "received": msg}
    elif data['io'] == "door":
        msg = "door open" if data['value'] == 1 else "door close"

        position = "DO" if data['value'] == 1 else "DC"
        url = f"http://{HOST}:{PORT}/{position}"
        requests.get(url)
        response = {"message": "Data received", "received": msg}

    elif data['io'] == "window":
        msg = "window open" if data['value'] == 1 else "window close"
        response = {"message": "Data received", "received": msg}

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)