from flask import Blueprint, request, jsonify
from services.memory_service import MemoryAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryController:
    def __init__(self):
        self.blueprint = Blueprint("memory_routes", __name__)
        self.blueprint.add_url_rule("/query/<content_type>/<mongo_doc_id>", view_func=self.query_content, methods=["GET"])
        self.blueprint.add_url_rule("/logs/<embedding_id>", view_func=self.get_logs, methods=["GET"])

    def query_content(self, content_type, mongo_doc_id):
        try:
            content = MemoryAgent.query_content_from_mongo(mongo_doc_id)
            if content and content.get("content_type") == content_type:
                return jsonify(content), 200
            else:
                return jsonify({"error": "Content not found or type mismatch."}), 404
        except Exception as e:
            logger.error(f"Error querying content: {e}")
            return jsonify({"error": "Failed to retrieve content."}), 500

    def get_logs(self, embedding_id):
        try:
            logs = MemoryAgent.query_action_logs(embedding_id)
            if logs:
                return jsonify(logs), 200
            else:
                return jsonify({"error": "No logs found for the specified embedding."}), 404
        except Exception as e:
            logger.error(f"Error retrieving logs: {e}")
            return jsonify({"error": "Failed to retrieve logs."}), 500

memory_controller = MemoryController()
memory_routes = memory_controller.blueprint
