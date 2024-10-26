from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import random
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'
db = SQLAlchemy(app)
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    option_1 = db.Column(db.String(255), nullable=False)
    option_2 = db.Column(db.String(255), nullable=False)
    option_3 = db.Column(db.String(255), nullable=False)
@app.before_request
def create_tables():
    db.create_all()
    if not Quiz.query.first():
        sample_quizzes = [
            Quiz(category="Category 1", question="Question 1?", answer="Answer 1", option_1="Option 1A", option_2="Option 1B", option_3="Option 1C"),
            Quiz(category="Category 1", question="Question 2?", answer="Answer 2", option_1="Option 2A", option_2="Option 2B", option_3="Option 2C"),
            Quiz(category="Category 2", question="Question 3?", answer="Answer 3", option_1="Option 3A", option_2="Option 3B", option_3="Option 3C"),
        ]
        db.session.bulk_save_objects(sample_quizzes)
        db.session.commit()
@app.route('/quiz/<category>', methods=['GET'])
def take_quiz(category):
    quizzes = Quiz.query.filter_by(category=category).all()
    if not quizzes:
        return jsonify({'message': 'No questions available in this category.'}), 404
    selected_quizzes = random.sample(quizzes, min(len(quizzes), 5))
    return jsonify([{'id': q.id, 'question': q.question, 'options': [q.option_1, q.option_2, q.option_3]} for q in selected_quizzes])
@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    user_answers = request.json.get('answers')
    score = 0
    for answer_data in user_answers:
        quiz = Quiz.query.get(answer_data['quiz_id'])
        if quiz and answer_data['selected_answer'] == quiz.answer:
            score += 1

    if 'user_id' in session:
        pass

    return jsonify({'score': score})
@app.route('/feedback', methods=['POST'])
def submit_feedback():
    feedback_data = request.json
    feedback_text = feedback_data.get('feedback')
    if feedback_text:
        return jsonify({'message': 'Feedback ba movafaghiat ezafe shod!'}), 201
    return jsonify({'message': 'Feedback nabayad khali bashe!'}), 400
if __name__ == 'main':
    app.run(debug=True)
