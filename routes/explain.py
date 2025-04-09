import logging
from datetime import datetime
from flask import Blueprint, render_template, request, flash, session
from services.gemini_client import GeminiClient
from services.file_processor import process_file_content
from models import (
    mongo, get_explanations, get_explanation, save_explanation, log_activity
)

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the blueprint
explain_bp = Blueprint('explain', __name__, url_prefix='/explain')

# Initialize Gemini Client
gemini_client = GeminiClient()

@explain_bp.route('/', methods=['GET'])
def explain_page():
    """Render the explain page."""
    # Get recent explanations
    recent_explanations = get_explanations(limit=5)
    return render_template('explain.html', recent_explanations=recent_explanations)

@explain_bp.route('/process', methods=['POST'])
def process_for_explanation():
    """Process a topic or concept for detailed explanation."""
    topic = request.form.get('topic')
    context = None
    
    # Check if we have a file upload for context
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        
        # Check file extension
        allowed_extensions = {'txt', 'pdf', 'docx'}
        filename = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if filename not in allowed_extensions:
            flash(f'File type not supported. Please upload {", ".join(allowed_extensions)} files', 'danger')
            recent_explanations = get_explanations(limit=5)
            return render_template('explain.html', recent_explanations=recent_explanations)
        
        try:
            # Process the file content for context
            context = process_file_content(file)
            session['last_content'] = context
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            flash(f'Error processing file: {str(e)}', 'danger')
            recent_explanations = get_explanations(limit=5)
            return render_template('explain.html', recent_explanations=recent_explanations)
    
    # If no file was uploaded, check if we have content in the session
    elif 'last_content' in session and session['last_content']:
        context = session['last_content']
    
    # If we have text input directly in the form
    elif request.form.get('context'):
        context = request.form.get('context')
        session['last_content'] = context
    
    # Make sure we have a topic to explain
    if not topic:
        flash('Please provide a topic or concept to explain', 'danger')
        recent_explanations = get_explanations(limit=5)
        return render_template('explain.html', recent_explanations=recent_explanations)
    
    try:
        # Generate explanation with Gemini AI
        explanation = gemini_client.generate_explanation(topic, context)
        
        # Save to database
        explanation_data = {
            'topic': topic,
            'context': context,
            'explanation_content': explanation,
            'created_at': datetime.utcnow()
        }
        explanation_id = save_explanation(explanation_data)
        
        # Log the activity
        activity_data = {
            'activity_type': 'explain',
            'description': f'Generated explanation for topic: {topic}',
            'reference_id': str(explanation_id),
            'reference_type': 'explanation',
            'created_at': datetime.utcnow()
        }
        log_activity(activity_data)
        
        # Get recent explanations
        recent_explanations = get_explanations(limit=5)
        
        return render_template(
            'explain.html', 
            topic=topic, 
            explanation=explanation,
            explanation_id=str(explanation_id),
            recent_explanations=recent_explanations
        )
    
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        flash(f'Error generating explanation: {str(e)}', 'danger')
        recent_explanations = get_explanations(limit=5)
        return render_template('explain.html', recent_explanations=recent_explanations)
