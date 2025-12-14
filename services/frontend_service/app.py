"""
Frontend Service - Веб-интерфейс приложения
"""

from flask import Flask, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# URL API Gateway для клиентской части
API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL', 'http://localhost:5000')


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html', api_gateway_url=API_GATEWAY_URL)


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    return {'status': 'healthy', 'service': 'frontend-service'}, 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)

