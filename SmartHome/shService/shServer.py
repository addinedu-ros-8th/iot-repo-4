from flask import Flask, request, jsonify
import serial

app = Flask(__name__)

@app.route('/send', methods=['POST'])
def receive_data():
    data = request.get_json()
    print(f"Received data: {data}")
    if data['io'] == "led":
        msg = "led ON" if data['value'] == 1 else "led OFF"
    elif data['io'] == "garage":
        msg = "garage open" if data['value'] == 1 else "garage close"
    elif data['io'] == "door":
        msg = "door open" if data['value'] == 1 else "door close"
    elif data['io'] == "window":
        msg = "window open" if data['value'] == 1 else "window close"
        
    response = {"message": "Data received", "received": msg}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000)