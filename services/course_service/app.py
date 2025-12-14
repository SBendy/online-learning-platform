"""
Course Service - Микросервис управления курсами
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests

app = Flask(__name__)

# Использовать базу данных в памяти для избежания проблем с правами доступа
db_uri = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
if ':memory:' in db_uri:
    print("Using in-memory database (data will be lost on restart)")
else:
    print(f"Database URI: {db_uri}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['AUTH_SERVICE_URL'] = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')

db = SQLAlchemy(app)


class Course(db.Model):
    """Модель курса"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=False)
    banner_image = db.Column(db.Text)  # Base64 изображение баннера


def validate_token(token):
    """Валидация токена через Auth Service"""
    try:
        response = requests.post(
            f"{app.config['AUTH_SERVICE_URL']}/validate",
            json={'token': token},
            timeout=2
        )
        if response.status_code == 200:
            return response.json().get('user')
        return None
    except:
        return None


def get_auth_header():
    """Получить токен из заголовка"""
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


def login_required(f):
    """Декоратор для проверки авторизации"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_auth_header()
        if not token:
            return jsonify({'error': 'Требуется авторизация'}), 401
        user = validate_token(token)
        if not user:
            return jsonify({'error': 'Неверный или истекший токен'}), 401
        # Сохраняем пользователя в kwargs
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    """Декоратор для проверки прав преподавателя"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_auth_header()
        if not token:
            return jsonify({'error': 'Требуется авторизация'}), 401
        user = validate_token(token)
        if not user:
            return jsonify({'error': 'Неверный или истекший токен'}), 401
        if user['role'] not in ['teacher', 'admin']:
            return jsonify({'error': 'Доступ запрещен'}), 403
        kwargs['current_user'] = user
        return f(*args, **kwargs)
    return decorated_function


def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        db.create_all()


@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья сервиса"""
    return jsonify({'status': 'healthy', 'service': 'course-service'}), 200


@app.route('/courses', methods=['GET'])
def get_courses():
    """Получить список всех опубликованных курсов"""
    courses = Course.query.filter_by(is_published=True).all()
    
    # Получение информации о создателях через Auth Service
    creator_ids = [course.creator_id for course in courses]
    creators_info = {}
    
    if creator_ids:
        try:
            response = requests.get(
                f"{app.config['AUTH_SERVICE_URL']}/users",
                timeout=2
            )
            if response.status_code == 200:
                users = response.json()
                creators_info = {u['id']: u['username'] for u in users}
        except:
            pass
    
    return jsonify([{
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'creator_id': course.creator_id,
        'creator': creators_info.get(course.creator_id, 'Неизвестно'),
        'created_at': course.created_at.isoformat(),
        'is_published': course.is_published,
        'banner_image': course.banner_image
    } for course in courses]), 200


@app.route('/courses/my', methods=['GET'])
@login_required
def get_my_courses(current_user=None):
    """Получить курсы текущего пользователя"""
    user_id = current_user['id']
    role = current_user['role']
    
    if role in ['teacher', 'admin']:
        courses = Course.query.filter_by(creator_id=user_id).all()
    else:
        # Для студентов нужно получить через Learning Service
        courses = []
    
    return jsonify([{
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'creator_id': course.creator_id,
        'created_at': course.created_at.isoformat(),
        'is_published': course.is_published,
        'banner_image': course.banner_image
    } for course in courses]), 200


@app.route('/courses', methods=['POST'])
@teacher_required
def create_course(current_user=None):
    """Создать новый курс (автоматически публикуется для всех студентов)"""
    data = request.json
    course = Course(
        title=data.get('title'),
        description=data.get('description'),
        creator_id=current_user['id'],
        is_published=data.get('is_published', True)  # По умолчанию публикуется
    )
    db.session.add(course)
    db.session.commit()
    
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'creator_id': course.creator_id,
        'is_published': course.is_published,
        'banner_image': course.banner_image,
        'message': 'Курс успешно создан и опубликован'
    }), 201


@app.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Получить информацию о курсе"""
    course = Course.query.get_or_404(course_id)
    
    # Проверка доступа для неопубликованных курсов
    if not course.is_published:
        token = get_auth_header()
        if token:
            user = validate_token(token)
            if user and (user['role'] in ['teacher', 'admin'] or course.creator_id == user['id']):
                pass
            else:
                return jsonify({'error': 'Курс не опубликован'}), 403
        else:
            return jsonify({'error': 'Курс не опубликован'}), 403
    
    # Получение информации о создателе
    creator_name = 'Неизвестно'
    try:
        response = requests.get(
            f"{app.config['AUTH_SERVICE_URL']}/user/{course.creator_id}",
            timeout=2
        )
        if response.status_code == 200:
            creator_name = response.json().get('username', 'Неизвестно')
    except:
        pass
    
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'creator_id': course.creator_id,
        'creator': creator_name,
        'created_at': course.created_at.isoformat(),
        'is_published': course.is_published,
        'banner_image': course.banner_image
    }), 200


@app.route('/courses/<int:course_id>', methods=['PUT'])
@teacher_required
def update_course(course_id, current_user=None):
    """Обновить курс"""
    course = Course.query.get_or_404(course_id)
    
    if course.creator_id != current_user['id'] and current_user['role'] != 'admin':
        return jsonify({'error': 'У вас нет прав на редактирование этого курса'}), 403
    
    data = request.json
    if 'title' in data:
        course.title = data['title']
    if 'description' in data:
        course.description = data['description']
    if 'is_published' in data:
        course.is_published = data['is_published']
    if 'banner_image' in data:
        course.banner_image = data['banner_image']
    
    db.session.commit()
    
    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'banner_image': course.banner_image,
        'message': 'Курс успешно обновлен'
    }), 200


@app.route('/courses/<int:course_id>', methods=['DELETE'])
@teacher_required
def delete_course(course_id, current_user=None):
    """Удалить курс"""
    course = Course.query.get_or_404(course_id)
    
    if course.creator_id != current_user['id'] and current_user['role'] != 'admin':
        return jsonify({'error': 'У вас нет прав на удаление этого курса'}), 403
    
    db.session.delete(course)
    db.session.commit()
    
    return jsonify({'message': 'Курс успешно удален'}), 200


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=True)

