from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
app = Flask(name)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, nullable=False)

@app.before_first_request
def create_tables():
    db.create_all()
    if not Question.query.first():
        sample_questions = [
            Question(question="Question 1?", answer="Answer 1", category_id=1),
            Question(question="Question 2?", answer="Answer 2", category_id=1),
            Question(question="Question 3?", answer="Answer 3", category_id=2),
        ]
        db.session.bulk_save_objects(sample_questions)
        db.session.commit()

@app.route('/quiz/<int:category_id>/<int:num_questions>', methods=['GET'])
def take_quiz(category_id, num_questions):
    questions = Question.query.filter_by(category_id=category_id).all()
    selected_questions = random.sample(questions, min(len(questions), num_questions))
    return jsonify([{'id': q.id, 'question': q.question} for q in selected_questions])

@app.route('/feedback', methods=['POST'])
def submit_feedback():
    feedback_data = request.json
    feedback_text = feedback_data.get('feedback')
    if feedback_text:
        return jsonify({'message': 'Feedback submitted successfully!'}), 201
    return jsonify({'message': 'Feedback cannot be empty!'}), 400

if name == 'main':
    app.run(debug=True)
