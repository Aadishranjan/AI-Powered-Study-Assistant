from config import MONGO_URI
import os
import logging
from flask import Flask, render_template

# Setup logging for easier debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure MongoDB
mongo_uri = MONGO_URI
app.config["MONGO_URI"] = mongo_uri

# Initialize MongoDB
from models import mongo
mongo.init_app(app)

# Try to connect to MongoDB
with app.app_context():
    try:
        # Test connection
        client = mongo.cx
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Set flag to indicate MongoDB is available
        app.config['MONGO_AVAILABLE'] = True
        
        # Create collections as needed when first documents are inserted
        # MongoDB automatically creates collections
        
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        # Set flag to indicate MongoDB is not available
        app.config['MONGO_AVAILABLE'] = False
        logger.warning("Running without database persistence. Data will not be saved between sessions.")

# Register blueprints
from routes.summarize import summarize_bp
from routes.quiz import quiz_bp
from routes.explain import explain_bp

app.register_blueprint(summarize_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(explain_bp)

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
