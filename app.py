from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, EqualTo
from functools import wraps
from models import db, User, Quiz, QuizAttempt
import random
from user_management import user_manager, Userr


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'



db.init_app(app)

# Form for registration
class RegisterForm(FlaskForm):
    username = StringField('نام کاربری', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('رمز عبور', validators=[InputRequired(), Length(min=4, max=20)])
    confirm_password = PasswordField('تایید رمز عبور', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('ثبت نام')

# Form for login
class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField('رمز عبور', validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField('ورود')

# Form for managing quizzes
class QuizForm(FlaskForm):
    category = StringField('دسته بندی', validators=[InputRequired()])
    question = StringField('سوال', validators=[InputRequired()])
    answer = StringField('جواب', validators=[InputRequired()])
    option_1 = StringField('گزینه ۱', validators=[InputRequired()])
    option_2 = StringField('گزینه ۲', validators=[InputRequired()])
    option_3 = StringField('گزینه ۳', validators=[InputRequired()])
    submit = SubmitField('ثبت')

# Decorator to restrict access to admin only
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') != 'admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


# Decorator to restrict access to logged in users only
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    return render_template('home.html', username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Special check for admin/admin
    if form.validate_on_submit():
        if form.username.data == "admin" and form.password.data == "admin":
            session['user_id'] = 1  # Or any suitable ID for admin
            session['username'] = 'admin'
            return redirect(url_for('admin_quiz_list'))

        # Regular user authentication
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
    
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Admin routes to manage quizzes
@app.route('/admin/quiz', methods=['GET'])
@admin_required
def admin_quiz_list():
    quizzes = Quiz.query.all()  # Get all quizzes
    return render_template('admin_quiz_list.html', quizzes=quizzes)

@app.route('/admin/quiz/add', methods=['GET', 'POST'])
@admin_required
def add_quiz():
    form = QuizForm()

    if form.validate_on_submit():
        new_quiz = Quiz(
            category=form.category.data,
            question=form.question.data,
            answer=form.answer.data,
            option_1=form.option_1.data,
            option_2=form.option_2.data,
            option_3=form.option_3.data
        )
        db.session.add(new_quiz)
        db.session.commit()
        return redirect(url_for('admin_quiz_list'))

    return render_template('quiz_form.html', form=form)

@app.route('/admin/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)

    if form.validate_on_submit():
        quiz.category = form.category.data
        quiz.question = form.question.data
        quiz.answer = form.answer.data
        quiz.option_1 = form.option_1.data
        quiz.option_2 = form.option_2.data
        quiz.option_3 = form.option_3.data
        db.session.commit()
        return redirect(url_for('admin_quiz_list'))

    return render_template('quiz_form.html', form=form)

@app.route('/admin/quiz/delete/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for('admin_quiz_list'))

@app.route('/admin/quiz/history')
@admin_required
def all_quiz_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Admin view shows all quiz attempts along with quiz details and user information
    attempts = db.session.query(
        QuizAttempt,
        User.username,
        Quiz.question,
        Quiz.category
    ).join(User).join(Quiz).all()

    return render_template('admin_quiz_history.html', attempts=attempts[::-1])


@app.route('/admin/users', methods=['GET'])
@admin_required
def admin_user_list():
    users = User.query.all()  # Get all users
    return render_template('admin_user_list.html', users=users[::-1])

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_user_list'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.username = request.form['username']  # Update username
        # Here, you might want to add additional fields for email, etc.
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

@app.route('/quiz')
@login_required
def quiz_categories():
    categories = db.session.query(Quiz.category).distinct().all()
    return render_template('categories.html', categories=categories[::-1])


@app.route('/quiz/<category>', methods=['GET', 'POST'])
@login_required
def quiz_titles(category):
    quizzes = Quiz.query.filter_by(category=category).all()
    if request.method == 'POST':
        score = 0
        for quiz in quizzes:
            selected_answer = request.form.get(f'answer_{quiz.id}')
            if selected_answer == quiz.answer:
                score += 1  # Count the correct answer

            # Save the attempt for each quiz
            if 'user_id' in session:
                new_attempt = QuizAttempt(user_id=session['user_id'], quiz_id=quiz.id, score=1 if selected_answer == quiz.answer else 0)
                db.session.add(new_attempt)

        db.session.commit()

        # Update user's score
        user = User.query.get(session['user_id'])
        user.score += score
        db.session.commit()

        return redirect(url_for('quiz_categories'))  # Redirect to categories or a summary page

    return render_template('quiz_titles.html', quizzes=quizzes, category=category[::-1])



@app.route('/quiz/history')
@login_required
def quiz_history():

    # Regular user view shows only their attempts along with quiz details
    user_id = session['user_id']
    attempts = db.session.query(
        QuizAttempt,
        User.username,
        Quiz.question,
        Quiz.category
    ).join(User).join(Quiz).filter(User.id == user_id).all()
    
    return render_template('quiz_history.html', attempts=attempts[::-1])

if __name__ == '__main__':
    app.run(debug=True)