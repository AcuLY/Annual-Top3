from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from io import BytesIO

app = Flask(__name__)

CORS(app, resources={r"/proxy/*": {"origins": "*"}})

@app.get('/proxy')
def proxy():
    image_url = request.args.get('url')
    
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        return send_file(
            BytesIO(response.content),
            mimetype=response.headers['Content-Type']
        )
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run()