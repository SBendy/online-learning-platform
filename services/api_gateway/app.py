"""
API Gateway - Микросервис маршрутизации запросов
"""

from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import requests
import os
import time
import socket

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# URL микросервисов
# В Docker Swarm можно использовать короткие имена (auth-service) или полные (learning-platform_auth-service)
STACK_NAME = os.environ.get('STACK_NAME', 'learning-platform')

def get_service_url(env_var, default_host, default_port, service_name):
    """Получить URL сервиса с поддержкой альтернативных имен в Swarm"""
    url = os.environ.get(env_var, f'http://{default_host}:{default_port}')
    
    # В Swarm используем полные имена по умолчанию, но также поддерживаем короткие
    # Если используется короткое имя сервиса, создаем альтернативное полное имя
    if f'://{service_name}:' in url:
        # Создаем альтернативное полное имя для Swarm
        alt_url = url.replace(f'://{service_name}:', f'://{STACK_NAME}_{service_name}:')
        # В Swarm пробуем сначала полное имя, потом короткое
        return alt_url, url
    elif f'://{STACK_NAME}_{service_name}:' in url:
        # Уже используется полное имя, создаем короткое как альтернативу
        short_url = url.replace(f'://{STACK_NAME}_{service_name}:', f'://{service_name}:')
        return url, short_url
    
    return url, None

AUTH_SERVICE, AUTH_SERVICE_ALT = get_service_url('AUTH_SERVICE_URL', 'localhost', '5001', 'auth-service')
COURSE_SERVICE, COURSE_SERVICE_ALT = get_service_url('COURSE_SERVICE_URL', 'localhost', '5002', 'course-service')
LEARNING_SERVICE, LEARNING_SERVICE_ALT = get_service_url('LEARNING_SERVICE_URL', 'localhost', '5003', 'learning-service')

# Логирование конфигурации
print(f"API Gateway Configuration:")
print(f"  AUTH_SERVICE: {AUTH_SERVICE} (alt: {AUTH_SERVICE_ALT})")
print(f"  COURSE_SERVICE: {COURSE_SERVICE} (alt: {COURSE_SERVICE_ALT})")
print(f"  LEARNING_SERVICE: {LEARNING_SERVICE} (alt: {LEARNING_SERVICE_ALT})")
print(f"  STACK_NAME: {STACK_NAME}")

# Функция для проверки доступности хоста
def check_host_resolvable(hostname, port, timeout=5):
    """Проверка, можно ли разрешить имя хоста"""
    try:
        # Извлекаем hostname из URL
        if '://' in hostname:
            hostname = hostname.split('://')[1].split(':')[0]
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False

# Логирование конфигурации при старте
print(f"API Gateway starting...")
print(f"AUTH_SERVICE: {AUTH_SERVICE}")
print(f"COURSE_SERVICE: {COURSE_SERVICE}")
print(f"LEARNING_SERVICE: {LEARNING_SERVICE}")

# Проверка доступности сервисов при старте (с задержкой для Swarm)
def wait_for_services():
    """Ожидание доступности сервисов"""
    max_wait = 60  # максимум 60 секунд
    wait_time = 0
    interval = 2
    
    services = [
        ('auth-service', AUTH_SERVICE),
        ('course-service', COURSE_SERVICE),
        ('learning-service', LEARNING_SERVICE)
    ]
    
    while wait_time < max_wait:
        all_ready = True
        for name, url in services:
            hostname = url.split('://')[1].split(':')[0] if '://' in url else url.split(':')[0]
            if not check_host_resolvable(hostname, None):
                print(f"Waiting for {name} ({hostname}) to be resolvable...")
                all_ready = False
                break
        
        if all_ready:
            print("All services are resolvable!")
            return True
        
        time.sleep(interval)
        wait_time += interval
    
    print("Warning: Some services may not be resolvable yet, but continuing...")
    return False

# Запуск проверки в фоновом режиме
import threading
threading.Thread(target=wait_for_services, daemon=True).start()


def proxy_request(service_url, path, method='GET', data=None, headers=None, retries=3, alt_url=None):
    """Проксирование запроса к микросервису с повторными попытками и fallback на альтернативный URL"""
    # В Swarm полные имена имеют приоритет, поэтому если есть альтернативный URL (который может быть полным),
    # пробуем его первым
    urls_to_try = []
    if alt_url and 'learning-platform_' in alt_url:
        # Если альтернативный URL содержит полное имя, пробуем его первым
        urls_to_try = [alt_url, service_url]
    else:
        urls_to_try = [service_url]
        if alt_url:
            urls_to_try.append(alt_url)
    
    # Подготовка headers
    request_headers = {'Content-Type': 'application/json'}
    if headers:
        request_headers.update(headers)
    
    last_error = None
    
    # Пробуем каждый URL
    for base_url in urls_to_try:
        url = f"{base_url}{path}"
        
        # Повторные попытки для каждого URL
        for attempt in range(retries):
            try:
                if method == 'GET':
                    response = requests.get(url, headers=request_headers, timeout=10)
                elif method == 'POST':
                    response = requests.post(url, json=data, headers=request_headers, timeout=10)
                elif method == 'PUT':
                    response = requests.put(url, json=data, headers=request_headers, timeout=10)
                elif method == 'DELETE':
                    response = requests.delete(url, headers=request_headers, timeout=10)
                else:
                    return jsonify({'error': 'Метод не поддерживается'}), 405
                
                # Обработка ответа
                try:
                    response_data = response.json()
                except ValueError:
                    response_data = {'error': 'Некорректный ответ от сервиса', 'status_code': response.status_code}
                
                return response_data, response.status_code
                
            except requests.exceptions.ConnectionError as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(1)  # Задержка перед повторной попыткой
                    continue
                # Если это последняя попытка для этого URL, пробуем следующий URL
                if base_url == urls_to_try[-1] and attempt == retries - 1:
                    # Это последний URL и последняя попытка
                    return jsonify({'error': f'Не удалось подключиться к сервису. Попробованы: {", ".join(urls_to_try)}. Ошибка: {str(e)}. Проверьте, что сервис запущен и доступен.'}), 503
                break  # Переходим к следующему URL
            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                if base_url == urls_to_try[-1] and attempt == retries - 1:
                    return jsonify({'error': f'Таймаут при подключении к сервису {base_url}'}), 504
                break
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                if base_url == urls_to_try[-1] and attempt == retries - 1:
                    return jsonify({'error': f'Ошибка связи с сервисом {base_url}: {str(e)}'}), 503
                break
    
    # Если все попытки исчерпаны
    return jsonify({'error': f'Не удалось подключиться к сервису после {retries} попыток для каждого URL. Последняя ошибка: {str(last_error)}'}), 503


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья gateway"""
    return jsonify({'status': 'healthy', 'service': 'api-gateway'}), 200


# Маршруты для Auth Service
@app.route('/api/auth/register', methods=['POST'])
def register():
    return proxy_request(AUTH_SERVICE, '/register', 'POST', request.json)


@app.route('/api/auth/login', methods=['POST'])
def login():
    return proxy_request(AUTH_SERVICE, '/login', 'POST', request.json, alt_url=AUTH_SERVICE_ALT)


@app.route('/api/auth/validate', methods=['POST'])
def validate():
    return proxy_request(AUTH_SERVICE, '/validate', 'POST', request.json, alt_url=AUTH_SERVICE_ALT)


@app.route('/api/auth/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(AUTH_SERVICE, f'/user/{user_id}', 'GET', headers=headers, alt_url=AUTH_SERVICE_ALT)


# Маршруты для Course Service
@app.route('/api/courses', methods=['GET'])
def get_courses():
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(COURSE_SERVICE, '/courses', 'GET', headers=headers, alt_url=COURSE_SERVICE_ALT)


@app.route('/api/courses/my', methods=['GET'])
def get_my_courses():
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(COURSE_SERVICE, '/courses/my', 'GET', headers=headers, alt_url=COURSE_SERVICE_ALT)


@app.route('/api/courses', methods=['POST'])
def create_course():
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(COURSE_SERVICE, '/courses', 'POST', request.json, headers=headers, alt_url=COURSE_SERVICE_ALT)


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(COURSE_SERVICE, f'/courses/{course_id}', 'GET', headers=headers, alt_url=COURSE_SERVICE_ALT)


@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(COURSE_SERVICE, f'/courses/{course_id}', 'PUT', request.json, headers=headers, alt_url=COURSE_SERVICE_ALT)


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(COURSE_SERVICE, f'/courses/{course_id}', 'DELETE', headers=headers, alt_url=COURSE_SERVICE_ALT)


# Маршруты для Learning Service
@app.route('/api/courses/<int:course_id>/lessons', methods=['GET'])
def get_lessons(course_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(LEARNING_SERVICE, f'/courses/{course_id}/lessons', 'GET', headers=headers, alt_url=LEARNING_SERVICE_ALT)


@app.route('/api/courses/<int:course_id>/lessons', methods=['POST'])
def create_lesson(course_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(LEARNING_SERVICE, f'/courses/{course_id}/lessons', 'POST', request.json, headers=headers, alt_url=LEARNING_SERVICE_ALT)


@app.route('/api/lessons/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(LEARNING_SERVICE, f'/lessons/{lesson_id}', 'GET', headers=headers, alt_url=LEARNING_SERVICE_ALT)


@app.route('/api/lessons/<int:lesson_id>', methods=['PUT'])
def update_lesson(lesson_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(LEARNING_SERVICE, f'/lessons/{lesson_id}', 'PUT', request.json, headers=headers, alt_url=LEARNING_SERVICE_ALT)


@app.route('/api/lessons/<int:lesson_id>', methods=['DELETE'])
def delete_lesson(lesson_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(LEARNING_SERVICE, f'/lessons/{lesson_id}', 'DELETE', headers=headers, alt_url=LEARNING_SERVICE_ALT)


@app.route('/api/courses/<int:course_id>/enroll', methods=['POST'])
def enroll_course(course_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(LEARNING_SERVICE, f'/courses/{course_id}/enroll', 'POST', headers=headers, alt_url=LEARNING_SERVICE_ALT)


@app.route('/api/users/<int:user_id>/enrollments', methods=['GET'])
def get_user_enrollments(user_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(LEARNING_SERVICE, f'/users/{user_id}/enrollments', 'GET', headers=headers, alt_url=LEARNING_SERVICE_ALT)


@app.route('/api/lessons/<int:lesson_id>/complete', methods=['POST'])
def complete_lesson(lesson_id):
    headers = {'Authorization': request.headers.get('Authorization', '')}
    return proxy_request(LEARNING_SERVICE, f'/lessons/{lesson_id}/complete', 'POST', headers=headers, alt_url=LEARNING_SERVICE_ALT)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

