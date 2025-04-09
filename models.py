"""Data models for the Study Assistant application using MongoDB."""
from datetime import datetime
from flask_pymongo import PyMongo

# Initialize PyMongo
mongo = PyMongo()

# Define model schemas as dictionaries to guide our MongoDB document structure
# These aren't enforced by MongoDB but serve as documentation for our code

SUMMARY_SCHEMA = {
    "title": str,  # Title of the summary
    "original_content": str,  # The original content that was summarized
    "summary_content": str,  # The generated summary
    "created_at": datetime,  # When the summary was created
    "file_type": str,  # File extension (pdf, txt, docx)
    "word_count": int  # Word count of the original content
}

QUIZ_SCHEMA = {
    "title": str,  # Title of the quiz
    "difficulty": str,  # Difficulty level (easy, medium, hard)
    "question_count": int,  # Number of questions
    "quiz_data": dict,  # The actual quiz questions, answers, and explanations
    "created_at": datetime  # When the quiz was created
}

QUIZ_ATTEMPT_SCHEMA = {
    "quiz_id": str,  # Reference to the quiz
    "score": int,  # Number of correct answers
    "max_score": int,  # Total number of questions
    "created_at": datetime  # When the attempt was made
}

EXPLANATION_SCHEMA = {
    "topic": str,  # The topic that was explained
    "context": str,  # Optional context provided
    "explanation_content": str,  # The generated explanation
    "created_at": datetime  # When the explanation was created
}

USER_ACTIVITY_SCHEMA = {
    "activity_type": str,  # Type of activity (summarize, quiz, explain)
    "description": str,  # Description of the activity
    "reference_id": str,  # Reference to related document
    "reference_type": str,  # Type of reference (summary, quiz, explanation)
    "created_at": datetime  # When the activity happened
}

# Helper functions for common database operations

def get_summaries(limit=None, sort_field='created_at', sort_direction=-1):
    """Get summaries from the database, newest first by default.
    
    Args:
        limit: Optional limit on number of results
        sort_field: Field to sort by
        sort_direction: 1 for ascending, -1 for descending
        
    Returns:
        List of summary documents or empty list if database not available
    """
    try:
        query = mongo.db.summaries.find().sort(sort_field, sort_direction)
        if limit:
            query = query.limit(limit)
        return list(query)
    except Exception:
        # Return empty list if database is not available
        return []

def get_summary(summary_id):
    """Get a specific summary by ID.
    
    Args:
        summary_id: The ObjectId of the summary
        
    Returns:
        The summary document or None
    """
    try:
        from bson.objectid import ObjectId
        return mongo.db.summaries.find_one({"_id": ObjectId(summary_id)})
    except Exception:
        # Return None if database is not available
        return None

def save_summary(summary_data):
    """Save a new summary to the database.
    
    Args:
        summary_data: Dictionary with summary data
        
    Returns:
        The inserted document ID or None if database is not available
    """
    try:
        # Ensure created_at is set
        if 'created_at' not in summary_data:
            summary_data['created_at'] = datetime.utcnow()
        
        result = mongo.db.summaries.insert_one(summary_data)
        return result.inserted_id
    except Exception:
        # Return None if database is not available
        return None

def get_quizzes(limit=None, sort_field='created_at', sort_direction=-1):
    """Get quizzes from the database, newest first by default."""
    try:
        query = mongo.db.quizzes.find().sort(sort_field, sort_direction)
        if limit:
            query = query.limit(limit)
        return list(query)
    except Exception:
        return []

def get_quiz(quiz_id):
    """Get a specific quiz by ID."""
    try:
        from bson.objectid import ObjectId
        return mongo.db.quizzes.find_one({"_id": ObjectId(quiz_id)})
    except Exception:
        return None

def save_quiz(quiz_data):
    """Save a new quiz to the database."""
    try:
        if 'created_at' not in quiz_data:
            quiz_data['created_at'] = datetime.utcnow()
        
        result = mongo.db.quizzes.insert_one(quiz_data)
        return result.inserted_id
    except Exception:
        return None

def get_explanations(limit=None, sort_field='created_at', sort_direction=-1):
    """Get explanations from the database, newest first by default."""
    try:
        query = mongo.db.explanations.find().sort(sort_field, sort_direction)
        if limit:
            query = query.limit(limit)
        return list(query)
    except Exception:
        return []

def get_explanation(explanation_id):
    """Get a specific explanation by ID."""
    try:
        from bson.objectid import ObjectId
        return mongo.db.explanations.find_one({"_id": ObjectId(explanation_id)})
    except Exception:
        return None

def save_explanation(explanation_data):
    """Save a new explanation to the database."""
    try:
        if 'created_at' not in explanation_data:
            explanation_data['created_at'] = datetime.utcnow()
        
        result = mongo.db.explanations.insert_one(explanation_data)
        return result.inserted_id
    except Exception:
        return None

def log_activity(activity_data):
    """Log a user activity."""
    try:
        if 'created_at' not in activity_data:
            activity_data['created_at'] = datetime.utcnow()
        
        result = mongo.db.user_activities.insert_one(activity_data)
        return result.inserted_id
    except Exception:
        return None