import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, session
from services.gemini_client import GeminiClient
from services.file_processor import process_file_content
from models import (
    mongo, get_quizzes, get_quiz, save_quiz, log_activity
)

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the blueprint
quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')

# Initialize Gemini Client
gemini_client = GeminiClient()

@quiz_bp.route('/', methods=['GET'])
def quiz_page():
    """Render the quiz page."""
    # Get recent quizzes
    recent_quizzes = get_quizzes(limit=5)
    return render_template('quiz.html', recent_quizzes=recent_quizzes)

@quiz_bp.route('/generate', methods=['POST'])
def generate_quiz():
    """Generate a quiz based on uploaded content or previously processed content."""
    content = None
    filename = "User Input"
    
    # Check if we have a file upload
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename
        
        # Check file extension
        allowed_extensions = {'txt', 'pdf', 'docx'}
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            flash(f'File type not supported. Please upload {", ".join(allowed_extensions)} files', 'danger')
            return render_template('quiz.html', recent_quizzes=get_quizzes(limit=5))
        
        try:
            # Process the file content
            content = process_file_content(file)
            session['last_content'] = content
            session['last_filename'] = filename
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'danger')
            return render_template('quiz.html', recent_quizzes=get_quizzes(limit=5))
    
    # If no file was uploaded, check if we have content in the session
    elif 'last_content' in session and session['last_content']:
        content = session['last_content']
        if 'last_filename' in session:
            filename = session['last_filename']
    
    # If we have text input directly in the form
    elif request.form.get('content'):
        content = request.form.get('content')
        session['last_content'] = content
    
    # If we still don't have content, show an error
    if not content:
        flash('Please upload a file or provide text to generate a quiz', 'danger')
        return render_template('quiz.html', recent_quizzes=get_quizzes(limit=5))
    
    # Get quiz options
    question_count = int(request.form.get('question_count', 5))
    difficulty = request.form.get('difficulty', 'medium')
    
    try:
        # Generate quiz with Gemini AI
        quiz_data = gemini_client.generate_quiz(content, question_count, difficulty)
        
        # Create quiz title
        title = f"Quiz on {filename}"
        
        # Save quiz to database
        quiz_obj = {
            'title': title,
            'difficulty': difficulty,
            'question_count': question_count,
            'quiz_data': quiz_data,
            'created_at': datetime.utcnow()
        }
        quiz_id = save_quiz(quiz_obj)
        
        # Log the activity
        activity_data = {
            'activity_type': 'quiz',
            'description': f'Generated quiz based on {filename}',
            'reference_id': str(quiz_id),
            'reference_type': 'quiz',
            'created_at': datetime.utcnow()
        }
        log_activity(activity_data)
        
        # Store in session for display
        session['current_quiz'] = quiz_data
        session['current_quiz_id'] = str(quiz_id)
        session['current_quiz_title'] = title
        
        # Get recent quizzes
        recent_quizzes = get_quizzes(limit=5)
        
        return render_template(
            'quiz.html', 
            quiz=quiz_data, 
            quiz_title=title,
            difficulty=difficulty,
            recent_quizzes=recent_quizzes
        )
    
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        flash(f'Error generating quiz: {str(e)}', 'danger')
        return render_template('quiz.html', recent_quizzes=get_quizzes(limit=5))

@quiz_bp.route('/submit', methods=['POST'])
def submit_quiz():
    """Handle quiz submission and score calculation."""
    try:
        # Get user answers from form
        user_answers = {}
        for key, value in request.form.items():
            if key.startswith('question-'):
                question_id = key.replace('question-', '')
                user_answers[question_id] = value
        
        # Get current quiz data from session
        quiz_data = session.get('current_quiz')
        quiz_id = session.get('current_quiz_id')
        
        if not quiz_data or not quiz_id:
            flash('Quiz data not found. Please generate a new quiz.', 'warning')
            return render_template('quiz.html', recent_quizzes=get_quizzes(limit=5))
        
        # Calculate score
        correct_count = 0
        total_questions = len(quiz_data['questions'])
        results = []
        
        for q_idx, question in enumerate(quiz_data['questions']):
            question_id = str(q_idx)
            user_answer = user_answers.get(question_id)
            correct_answer = question['answer']
            
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1
            
            results.append({
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'explanation': question.get('explanation', '')
            })
        
        # Calculate percentage
        score_percent = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
        
        # Save quiz attempt
        try:
            quiz_attempt = {
                'quiz_id': quiz_id,
                'score': correct_count,
                'max_score': total_questions,
                'created_at': datetime.utcnow()
            }
            mongo.db.quiz_attempts.insert_one(quiz_attempt)
        except Exception as e:
            logger.warning(f"Failed to save quiz attempt: {str(e)}")
        
        # Return results
        return render_template(
            'quiz.html',
            quiz_results=results,
            score=correct_count,
            total=total_questions,
            percent=score_percent,
            quiz_title=session.get('current_quiz_title'),
            recent_quizzes=get_quizzes(limit=5)
        )
    
    except Exception as e:
        logger.error(f"Error processing quiz submission: {str(e)}")
        flash(f'Error processing your quiz submission: {str(e)}', 'danger')
        return render_template('quiz.html', recent_quizzes=get_quizzes(limit=5))
