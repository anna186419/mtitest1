from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    teacher = db.relationship('Teacher', backref='courses')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    students = Student.query.all()
    teachers = Teacher.query.all()
    courses = Course.query.all() if current_user.is_authenticated else []
    return render_template('index.html', teachers=teachers, students=students, courses=courses)
@app.route('/add_student', methods=['GET', 'POST'])
@login_required  # если хотите, чтобы доступ был только для авторизованных пользователей
def add_student():
    if request.method == 'POST':
        student_name = request.form['name']
        new_student = Student(name=student_name)
        db.session.add(new_student)
        db.session.commit()
        flash('Студент добавлен!', 'success')
        return redirect(url_for('index'))
    return render_template('add_student.html')  # Создайте этот шаблон

@app.route('/add_teacher', methods=['GET', 'POST'])
@login_required  # Если хотите, чтобы доступ был только для авторизованных пользователей
def add_teacher():
    if request.method == 'POST':
        teacher_name = request.form['name']
        new_teacher = Teacher(name=teacher_name)
        db.session.add(new_teacher)
        db.session.commit()
        flash('Преподаватель добавлен!', 'success')
        return redirect(url_for('index'))
    return render_template('add_teacher.html')  # Создайте этот шаблон

@app.route('/add_course', methods=['GET', 'POST'])
@login_required  # Если хотите, чтобы доступ был только для авторизованных пользователей
def add_course():
    if request.method == 'POST':
        course_name = request.form['name']
        new_course = Course(name=course_name)
        db.session.add(new_course)
        db.session.commit()
        flash('Курс добавлен!', 'success')
        return redirect(url_for('index'))
    return render_template('add_course.html')  # Создайте этот шаблон

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash('Registration Successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    if not inspector.has_table('student'):  # Проверяем наличие таблицы 'student'
        db.create_all()
