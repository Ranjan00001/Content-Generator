from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from routes.presentation_routes import presentation_routes
from routes.blog_routes import blog_routes
from utils.database import db

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# CORS Configuration
CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:5173"]}},
    supports_credentials=True,
    expose_headers=["Content-Type", "Authorization"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS", "DELETE", "PUT"],
)

# Register Blueprints
app.register_blueprint(presentation_routes, url_prefix="/api/v1/presentations")
app.register_blueprint(blog_routes, url_prefix="/api/v1/blog")
# app.register_blueprint(chat_routes, url_prefix="/api/v1/chat")
# app.register_blueprint(reel_routes, url_prefix="/api/v1/reels")
# app.register_blueprint(image_routes, url_prefix="/api/v1/images")
# app.register_blueprint(video_routes, url_prefix="/api/v1/videos")


@app.before_request
def handle_preflight():
    """Handle CORS preflight requests."""
    if request.method == "OPTIONS":
        response = jsonify({"message": "Preflight OK"})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


@app.route("/")
def index():
    """Root endpoint."""
    return jsonify({"message": "Welcome to the Content Generation API!"})


# Table creation on application startup
with app.app_context():
    try:
        db.create_all()  # Create all tables if they don't exist
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Use PORT from environment or default to 5000
    app.run(debug=True, port=port)
