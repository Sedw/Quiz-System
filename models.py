from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, default=0)
    attempts = db.relationship('QuizAttempt', back_populates='user', cascade='all, delete-orphan')  # Relationship with QuizAttempt

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    question = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(200), nullable=False)
    option_1 = db.Column(db.String(200), nullable=False)
    option_2 = db.Column(db.String(200), nullable=False)
    option_3 = db.Column(db.String(200), nullable=False)

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='attempts')  # Relationship with User
    quiz = db.relationship('Quiz')  # Optional, if you want to reference Quiz