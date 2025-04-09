import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, session, redirect, url_for
from werkzeug.utils import secure_filename
from services.gemini_client import GeminiClient
from services.file_processor import process_file_content, get_file_content_summary
from models import (
    mongo, get_summaries, get_summary, save_summary, log_activity
)

# Setup logging
logger = logging.getLogger(__name__)

# Initialize the blueprint
summarize_bp = Blueprint('summarize', __name__, url_prefix='/summarize')

# Initialize Gemini Client
gemini_client = GeminiClient()

@summarize_bp.route('/', methods=['GET'])
def summarize_page():
    """Render the summarize page."""
    # Get the most recent summaries for display
    recent_summaries = get_summaries(limit=5)
    return render_template('summarize.html', recent_summaries=recent_summaries)

@summarize_bp.route('/process', methods=['POST'])
def process_for_summary():
    """Process uploaded file and generate a summary."""
    if 'file' not in request.files:
        flash('No file part', 'danger')
        recent_summaries = get_summaries(limit=5)
        return render_template('summarize.html', recent_summaries=recent_summaries)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        recent_summaries = get_summaries(limit=5)
        return render_template('summarize.html', recent_summaries=recent_summaries)
    
    # Check file extension
    allowed_extensions = {'txt', 'pdf', 'docx'}
    filename = secure_filename(file.filename)
    file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_extension not in allowed_extensions:
        flash(f'File type not supported. Please upload {", ".join(allowed_extensions)} files', 'danger')
        recent_summaries = get_summaries(limit=5)
        return render_template('summarize.html', recent_summaries=recent_summaries)
    
    try:
        # Process file content
        content = process_file_content(file)
        
        # Generate summary with Gemini AI
        summary = gemini_client.generate_summary(content)
        
        # Store in session for potential later use
        session['last_content'] = content
        session['last_summary'] = summary
        
        # Save to database
        summary_data = {
            'title': filename,
            'original_content': content,
            'summary_content': summary,
            'file_type': file_extension,
            'word_count': len(content.split()),
            'created_at': datetime.utcnow()
        }
        summary_id = save_summary(summary_data)
        
        # Log the activity if database is available
        if summary_id:
            activity_data = {
                'activity_type': 'summarize',
                'description': f'Generated summary for {filename}',
                'reference_id': str(summary_id),
                'reference_type': 'summary',
                'created_at': datetime.utcnow()
            }
            log_activity(activity_data)
        
        # Get recent summaries for display
        recent_summaries = get_summaries(limit=5)
        
        template_args = {
            'summary': summary,
            'filename': filename,
            'recent_summaries': recent_summaries
        }
        
        # Only add summary_id if database save was successful
        if summary_id:
            template_args['summary_id'] = str(summary_id)
            
        return render_template('summarize.html', **template_args)
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        flash(f'Error processing file: {str(e)}', 'danger')
        recent_summaries = get_summaries(limit=5)
        return render_template('summarize.html', recent_summaries=recent_summaries)

@summarize_bp.route('/history', methods=['GET'])
def summary_history():
    """Show history of summaries."""
    summaries = get_summaries()
    return render_template('summary_history.html', summaries=summaries)

@summarize_bp.route('/view/<summary_id>', methods=['GET'])
def view_summary(summary_id):
    """View a specific summary."""
    summary_doc = get_summary(summary_id)
    if not summary_doc:
        flash("Summary not found", "danger")
        return redirect(url_for('summarize.summary_history'))
    
    return render_template(
        'view_summary.html', 
        summary=summary_doc['summary_content'], 
        filename=summary_doc['title'],
        original_content=summary_doc['original_content'],
        created_at=summary_doc['created_at']
    )
