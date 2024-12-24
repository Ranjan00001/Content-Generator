from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from routes.presentation_routes import presentation_routes
from routes.blog_routes import blog_routes
# from routes.chat_routes import chat_routes
# from routes.reel_routes import reel_routes
# from routes.image_routes import image_routes
# from routes.video_routes import video_routes

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
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
    if request.method == "OPTIONS":
        response = jsonify({"message": "Preflight OK"})
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response, 200
    
# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
