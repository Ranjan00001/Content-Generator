from flask import Blueprint, request, jsonify, send_file, json
# from services.presentation_service import create_presentation, fetch_content_from_gemini
from services.presentation_service import PresentationService
from dotenv import load_dotenv
import logging, os, uuid
from configs.config import themes, supported_layouts

load_dotenv()
GENERATED_FILES_DIR = os.getenv("STORAGE_PATH")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PresentationController:
    def __init__(self):
        self.blueprint = Blueprint("presentation_routes", __name__)
        self.blueprint.add_url_rule("/", view_func=self.create_presentation, methods=["POST"])
        self.blueprint.add_url_rule("/<presentation_id>", view_func=self.get_presentation_details, methods=["GET"])
        self.blueprint.add_url_rule("/<presentation_id>/download", view_func=self.download_presentation, methods=["GET"])
        self.blueprint.add_url_rule("/<presentation_id>/configure", view_func=self.configure_presentation, methods=["POST"])

    def _validate_request(self, data):
        topic = data.get("topic")
        num_slides = data.get("num_slides", 5)
        layouts = data.get("layouts", [])

        if not topic:
            return {"error": "Topic is required"}, 400

        if not isinstance(num_slides, int) or not (1 <= num_slides <= 20):
            return {"error": "num_slides must be an integer between 1 and 20"}, 400

        if not isinstance(layouts, list):
            return {"error": "layouts must be a list"}, 400

        for layout in layouts:
            if layout not in supported_layouts:
                return {"error": f"Unsupported layout type: {layout}"}, 400

        return None, 200

    def _extend_or_trim_layouts(self, layouts, num_slides):
        if len(layouts) < num_slides:
            layouts.extend(["bullet_points"] * (num_slides - len(layouts)))
        elif len(layouts) > num_slides:
            layouts = layouts[:num_slides]
        return layouts

    def _save_presentation(self, prs, presentation_id):
        pptx_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.pptx")
        try:
            with open(pptx_path, 'wb') as pptx_file:
                prs.save(pptx_file)
            return pptx_path
        except Exception as e:
            logger.error("Error saving presentation file: %s", e)
            raise

    def _save_presentation_details(self, presentation_id, details):
        json_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.json")
        try:
            with open(json_path, 'w') as json_file:
                json.dump(details, json_file, indent=4)
        except Exception as e:
            logger.error("Error saving presentation details: %s", e)
            raise

    def _load_presentation_details(self, presentation_id):
        json_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.json")
        if not os.path.exists(json_path):
            logger.info("Presentation ID %s does not exist", presentation_id)
            return None
        try:
            with open(json_path, 'r') as json_file:
                return json.load(json_file)
        except Exception as e:
            logger.error("Error reading presentation details: %s", e)
            raise

    def create_presentation(self):
        data = request.json

        validation_error, status_code = self._validate_request(data)
        if validation_error:
            return jsonify(validation_error), status_code

        topic = data["topic"]
        num_slides = data.get("num_slides", 5)
        theme = data.get("theme", "default")
        layouts = self._extend_or_trim_layouts(data.get("layouts", []), num_slides)

        try:
            content = service.fetch_content_from_gemini(topic, num_slides, layouts)
            # print('here',content)
            prs = service.create_presentation(content, theme_name=theme)
        except Exception as e:
            logger.error("Error creating presentation: %s", e)
            return jsonify({"error": "Failed to create presentation"}), 500

        presentation_id = str(uuid.uuid4())
        try:
            self._save_presentation(prs, presentation_id)   # Saving .pptx file
            presentation_details = {
                "id": presentation_id,
                "topic": topic,
                "num_slides": num_slides,
                "theme": theme,
                "layouts": layouts,
                "status": "created",
                "download_url": f"/api/v1/presentations/{presentation_id}/download",
                # "silde_data": content
            }
            self._save_presentation_details(presentation_id, presentation_details)  # Saving the metadata about slide
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify(presentation_details), 201

    def get_presentation_details(self, presentation_id):
        presentation_details = self._load_presentation_details(presentation_id)
        if not presentation_details:
            return jsonify({"error": "Presentation not found"}), 404
        return jsonify(presentation_details), 200

    def download_presentation(self, presentation_id):
        pptx_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.pptx")
        if os.path.exists(pptx_path):
            return send_file(pptx_path, as_attachment=True)
        return jsonify({"error": "Presentation not found"}), 404

    def configure_presentation(self, presentation_id):
        presentation_details = self._load_presentation_details(presentation_id)
        if not presentation_details:
            return jsonify({"error": "Presentation not found"}), 404

        data = request.json
        if "topic" in data:
            presentation_details["topic"] = data["topic"]

        if "num_slides" in data:
            num_slides = data["num_slides"]
            if not isinstance(num_slides, int) or not (1 <= num_slides <= 20):
                return jsonify({"error": "num_slides must be an integer between 1 and 20"}), 400
            presentation_details["num_slides"] = num_slides
        else:
            num_slides = presentation_details["num_slides"]

        if "theme" in data:
            theme = data["theme"]
            if theme not in themes:
                return jsonify({"error": f"Unsupported theme: {theme}"}), 400
            presentation_details["theme"] = theme
        else:
            theme = presentation_details["theme"]

        if "layouts" in data:
            layouts = data["layouts"]
            if not isinstance(layouts, list):
                return jsonify({"error": "layouts must be a list"}), 400
            for layout in layouts:
                if layout not in supported_layouts:
                    return jsonify({"error": f"Unsupported layout type: {layout}"}), 400
            layouts = self._extend_or_trim_layouts(layouts, num_slides)
            presentation_details["layouts"] = layouts
        else:
            layouts = presentation_details["layouts"]

        try:
            content = service.fetch_content_from_gemini(presentation_details["topic"], num_slides, layouts)
            prs = service.create_presentation(content, theme_name=theme)
            self._save_presentation(prs, presentation_id)
            presentation_details["status"] = "updated"
            self._save_presentation_details(presentation_id, presentation_details)
        except Exception as e:
            logger.error("Error configuring presentation: %s", e)
            return jsonify({"error": str(e)}), 500

        return jsonify(presentation_details), 200

service = PresentationService()
presentation_controller = PresentationController()
presentation_routes = presentation_controller.blueprint
