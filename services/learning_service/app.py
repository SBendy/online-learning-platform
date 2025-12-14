"""
Learning Service - Микросервис управления уроками и прогрессом обучения
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import requests
import base64
import json

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
app.config['COURSE_SERVICE_URL'] = os.environ.get('COURSE_SERVICE_URL', 'http://localhost:5002')

db = SQLAlchemy(app)


class Lesson(db.Model):
    """Модель урока"""
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    images = db.Column(db.Text)  # JSON список изображений (base64 или URL)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_images(self):
        """Получить список изображений"""
        if self.images:
            try:
                return json.loads(self.images)
            except:
                return []
        return []
    
    def set_images(self, images_list):
        """Установить список изображений"""
        self.images = json.dumps(images_list) if images_list else None


class Enrollment(db.Model):
    """Модель записи на курс"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='unique_enrollment'),)


class LessonProgress(db.Model):
    """Модель прогресса по уроку"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    lesson_id = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='unique_lesson_progress'),)


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
    return jsonify({'status': 'healthy', 'service': 'learning-service'}), 200


@app.route('/courses/<int:course_id>/lessons', methods=['GET'])
def get_lessons(course_id):
    """Получить список уроков курса"""
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    
    return jsonify([{
        'id': lesson.id,
        'course_id': lesson.course_id,
        'title': lesson.title,
        'content': lesson.content,
        'images': lesson.get_images(),
        'order': lesson.order,
        'created_at': lesson.created_at.isoformat()
    } for lesson in lessons]), 200


@app.route('/courses/<int:course_id>/lessons', methods=['POST'])
@teacher_required
def create_lesson(course_id, current_user=None):
    """Создать урок в курсе"""
    # Проверка существования курса через Course Service
    try:
        response = requests.get(
            f"{app.config['COURSE_SERVICE_URL']}/courses/{course_id}",
            headers={'Authorization': f"Bearer {get_auth_header()}"},
            timeout=2
        )
        if response.status_code != 200:
            return jsonify({'error': 'Курс не найден'}), 404
        
        course = response.json()
        if course['creator_id'] != current_user['id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'У вас нет прав на редактирование этого курса'}), 403
    except:
        return jsonify({'error': 'Ошибка связи с сервисом курсов'}), 500
    
    data = request.json
    existing_lessons = Lesson.query.filter_by(course_id=course_id).count()
    
    # Обработка изображений
    images = data.get('images', [])
    if isinstance(images, list):
        # Если изображения переданы как base64, сохраняем их
        processed_images = []
        for img in images:
            if isinstance(img, dict):
                # Формат: {"data": "base64...", "type": "image/png", "name": "image.png"}
                processed_images.append(img)
            elif isinstance(img, str):
                # Просто base64 строка
                processed_images.append({"data": img, "type": "image/png"})
        images = processed_images
    
    lesson = Lesson(
        course_id=course_id,
        title=data.get('title'),
        content=data.get('content'),
        order=data.get('order', existing_lessons)
    )
    lesson.set_images(images)
    db.session.add(lesson)
    db.session.commit()
    
    return jsonify({
        'id': lesson.id,
        'title': lesson.title,
        'content': lesson.content,
        'images': lesson.get_images(),
        'order': lesson.order,
        'message': 'Урок успешно создан'
    }), 201


@app.route('/lessons/<int:lesson_id>', methods=['GET'])
@login_required
def get_lesson(lesson_id):
    """Получить информацию об уроке"""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Проверка доступа к курсу
    try:
        response = requests.get(
            f"{app.config['COURSE_SERVICE_URL']}/courses/{lesson.course_id}",
            headers={'Authorization': f"Bearer {get_auth_header()}"},
            timeout=2
        )
        if response.status_code != 200:
            return jsonify({'error': 'Курс не найден'}), 404
    except:
        return jsonify({'error': 'Ошибка связи с сервисом курсов'}), 500
    
    return jsonify({
        'id': lesson.id,
        'course_id': lesson.course_id,
        'title': lesson.title,
        'content': lesson.content,
        'images': lesson.get_images(),
        'order': lesson.order,
        'created_at': lesson.created_at.isoformat()
    }), 200


@app.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id, current_user=None):
    """Записаться на курс"""
    user_id = current_user['id']
    
    # Проверка существования курса
    try:
        response = requests.get(
            f"{app.config['COURSE_SERVICE_URL']}/courses/{course_id}",
            timeout=2
        )
        if response.status_code != 200:
            return jsonify({'error': 'Курс не найден'}), 404
        
        course = response.json()
        if not course.get('is_published'):
            return jsonify({'error': 'Курс не опубликован'}), 400
    except:
        return jsonify({'error': 'Ошибка связи с сервисом курсов'}), 500
    
    existing = Enrollment.query.filter_by(user_id=user_id, course_id=course_id).first()
    if existing:
        return jsonify({'error': 'Вы уже записаны на этот курс'}), 400
    
    enrollment = Enrollment(user_id=user_id, course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    
    return jsonify({'message': 'Вы успешно записались на курс'}), 201


@app.route('/courses/<int:course_id>/enrollments', methods=['GET'])
@login_required
def get_enrollments(course_id):
    """Получить записи на курс"""
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    
    return jsonify([{
        'id': e.id,
        'user_id': e.user_id,
        'course_id': e.course_id,
        'progress': e.progress,
        'enrolled_at': e.enrolled_at.isoformat()
    } for e in enrollments]), 200


@app.route('/users/<int:user_id>/enrollments', methods=['GET'])
@login_required
def get_user_enrollments(user_id, current_user=None):
    """Получить курсы пользователя"""
    if current_user['id'] != user_id and current_user['role'] not in ['admin']:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    enrollments = Enrollment.query.filter_by(user_id=user_id).all()
    
    # Получение информации о курсах
    courses_info = []
    for enrollment in enrollments:
        try:
            response = requests.get(
                f"{app.config['COURSE_SERVICE_URL']}/courses/{enrollment.course_id}",
                timeout=2
            )
            if response.status_code == 200:
                course = response.json()
                courses_info.append({
                    'course_id': course['id'],
                    'title': course['title'],
                    'description': course['description'],
                    'progress': enrollment.progress,
                    'enrolled_at': enrollment.enrolled_at.isoformat()
                })
        except:
            pass
    
    return jsonify(courses_info), 200


@app.route('/lessons/<int:lesson_id>', methods=['PUT'])
@teacher_required
def update_lesson(lesson_id, current_user=None):
    """Обновить урок"""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Проверка прав на курс
    try:
        response = requests.get(
            f"{app.config['COURSE_SERVICE_URL']}/courses/{lesson.course_id}",
            headers={'Authorization': f"Bearer {get_auth_header()}"},
            timeout=2
        )
        if response.status_code != 200:
            return jsonify({'error': 'Курс не найден'}), 404
        
        course = response.json()
        if course['creator_id'] != current_user['id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'У вас нет прав на редактирование этого урока'}), 403
    except:
        return jsonify({'error': 'Ошибка связи с сервисом курсов'}), 500
    
    data = request.json
    if 'title' in data:
        lesson.title = data['title']
    if 'content' in data:
        lesson.content = data['content']
    if 'images' in data:
        images = data['images']
        if isinstance(images, list):
            processed_images = []
            for img in images:
                if isinstance(img, dict):
                    processed_images.append(img)
                elif isinstance(img, str):
                    processed_images.append({"data": img, "type": "image/png"})
            lesson.set_images(processed_images)
    if 'order' in data:
        lesson.order = data['order']
    
    db.session.commit()
    
    return jsonify({
        'id': lesson.id,
        'title': lesson.title,
        'content': lesson.content,
        'images': lesson.get_images(),
        'order': lesson.order,
        'message': 'Урок успешно обновлен'
    }), 200


@app.route('/lessons/<int:lesson_id>', methods=['DELETE'])
@teacher_required
def delete_lesson(lesson_id, current_user=None):
    """Удалить урок"""
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Проверка прав на курс
    try:
        response = requests.get(
            f"{app.config['COURSE_SERVICE_URL']}/courses/{lesson.course_id}",
            headers={'Authorization': f"Bearer {get_auth_header()}"},
            timeout=2
        )
        if response.status_code != 200:
            return jsonify({'error': 'Курс не найден'}), 404
        
        course = response.json()
        if course['creator_id'] != current_user['id'] and current_user['role'] != 'admin':
            return jsonify({'error': 'У вас нет прав на удаление этого урока'}), 403
    except:
        return jsonify({'error': 'Ошибка связи с сервисом курсов'}), 500
    
    db.session.delete(lesson)
    db.session.commit()
    
    return jsonify({'message': 'Урок успешно удален'}), 200


@app.route('/lessons/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id, current_user=None):
    """Отметить урок как пройденный"""
    lesson = Lesson.query.get_or_404(lesson_id)
    user_id = current_user['id']
    
    # Проверка записи на курс
    enrollment = Enrollment.query.filter_by(user_id=user_id, course_id=lesson.course_id).first()
    if not enrollment:
        return jsonify({'error': 'Вы не записаны на этот курс'}), 400
    
    # Проверка, не пройден ли уже урок
    existing_progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if existing_progress:
        return jsonify({'message': 'Урок уже пройден', 'progress': enrollment.progress}), 200
    
    # Создание записи о прогрессе
    progress = LessonProgress(user_id=user_id, lesson_id=lesson_id)
    db.session.add(progress)
    
    # Обновление общего прогресса
    total_lessons = Lesson.query.filter_by(course_id=lesson.course_id).count()
    completed_lessons = LessonProgress.query.filter_by(user_id=user_id).join(
        Lesson, LessonProgress.lesson_id == Lesson.id
    ).filter(Lesson.course_id == lesson.course_id).count()
    
    if total_lessons > 0:
        enrollment.progress = int((completed_lessons + 1) / total_lessons * 100)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Урок отмечен как пройденный',
        'progress': enrollment.progress
    }), 200


if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=True)

