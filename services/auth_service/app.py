"""
Auth Service - Микросервис аутентификации и авторизации
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
import os

app = Flask(__name__)

# Поддержка Docker secrets: читаем из файла, если доступен, иначе из переменной окружения
JWT_SECRET_FILE = os.environ.get('JWT_SECRET_FILE')
if JWT_SECRET_FILE and os.path.exists(JWT_SECRET_FILE):
    with open(JWT_SECRET_FILE, 'r') as f:
        app.config['SECRET_KEY'] = f.read().strip()
else:
    app.config['SECRET_KEY'] = os.environ.get('JWT_SECRET', 'jwt-secret-key-change-in-production')

# Использовать базу данных в памяти для избежания проблем с правами доступа
# В production можно переключиться на файловую базу данных
db_uri = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
if ':memory:' in db_uri:
    print("Using in-memory database (data will be lost on restart)")
else:
    print(f"Database URI: {db_uri}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    """Модель пользователя"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
        # Создать тестового преподавателя
        if not User.query.filter_by(username='teacher').first():
            teacher = User(
                username='teacher',
                email='teacher@example.com',
                password_hash=generate_password_hash('teacher123'),
                role='teacher'
            )
            db.session.add(teacher)
            db.session.commit()
            print("Тестовый преподаватель создан: teacher / teacher123")


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    return jsonify({'status': 'healthy', 'service': 'auth-service'}), 200


@app.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')
    
    if not username or not email or not password:
        return jsonify({'error': 'Не все поля заполнены'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Пользователь с таким именем уже существует'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Пользователь с таким email уже существует'}), 400
    
    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        role=role
    )
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Пользователь успешно зарегистрирован',
        'user_id': user.id,
        'username': user.username,
        'role': user.role
    }), 201


@app.route('/login', methods=['POST'])
def login():
    """Вход в систему и получение JWT токена"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Необходимо указать имя пользователя и пароль'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if user and check_password_hash(user.password_hash, password):
        # Генерация JWT токена
        token = jwt.encode({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            'message': 'Успешный вход',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
    
    return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401


@app.route('/validate', methods=['POST'])
def validate_token():
    """Валидация JWT токена"""
    token = request.json.get('token')
    
    if not token:
        return jsonify({'error': 'Токен не предоставлен'}), 400
    
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        
        if not user:
            return jsonify({'error': 'Пользователь не найден'}), 404
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role
            }
        }), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Токен истек'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Неверный токен'}), 401


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Получить информацию о пользователе"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at.isoformat()
    }), 200


@app.route('/users', methods=['GET'])
def get_users():
    """Получить список пользователей (для внутренних сервисов)"""
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    } for user in users]), 200


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

