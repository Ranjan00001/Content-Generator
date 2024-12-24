from flask import Blueprint, request, jsonify, send_file, json
from services.presentation_service import create_presentation, save_presentation, fetch_content_from_gemini
from dotenv import load_dotenv
import logging, os, uuid
from configs.config import themes

load_dotenv()
GENERATED_FILES_DIR = os.getenv("STORAGE_PATH")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

presentation_routes = Blueprint("presentation_routes", __name__)
@presentation_routes.route("/", methods=["POST"])
def create_presentation_route():
    """
    Creates a new presentation based on the provided topic, number of slides, theme, and layouts.
    """
    data = request.json
    topic = data.get("topic")
    num_slides = data.get("num_slides", 5)
    theme = data.get("theme", "default")
    layouts = data.get("layouts", [])

    # Input Validation
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    if not isinstance(num_slides, int) or not (1 <= num_slides <= 20):
        return jsonify({"error": "num_slides must be an integer between 1 and 20"}), 400

    supported_layouts = {"title", "bullet_points", "two_column", "content_with_image"}

    # Validate layouts
    if not isinstance(layouts, list):
        return jsonify({"error": "layouts must be a list"}), 400

    for layout in layouts:
        if layout not in supported_layouts:
            return jsonify({"error": f"Unsupported layout type: {layout}"}), 400

    # If layouts list is shorter than num_slides, fill the rest with 'bullet_points'
    if len(layouts) < num_slides:
        layouts.extend(["bullet_points"] * (num_slides - len(layouts)))
    elif len(layouts) > num_slides:
        layouts = layouts[:num_slides]

    # Fetch content using Gemini
    try:
        content = fetch_content_from_gemini(topic, num_slides, layouts)
        # logger.info("Final content before creating presentation: %s", content)
    except Exception as e:
        logger.error("Error fetching content: %s", e)
        return jsonify({"error": str(e)}), 500

    # Create the presentation
    try:
        prs = create_presentation(content, theme_name=theme)
    except Exception as e:
        logger.error("Error creating presentation: %s", e)
        return jsonify({"error": "Failed to create presentation"}), 500

    # Save the PPTX file
    presentation_id = str(uuid.uuid4())
    pptx_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.pptx")
    try:
        prs.save(pptx_path)
    except Exception as e:
        logger.error("Error saving presentation file: %s", e)
        return jsonify({"error": "Failed to save presentation file"}), 500

    # Save the presentation details in a JSON file
    presentation_details = {
        "id": presentation_id,
        "topic": topic,
        "num_slides": num_slides,
        "theme": theme,
        "layouts": layouts,
        "status": "created",
        "download_url": f"/api/v1/presentations/{presentation_id}/download",
    }

    json_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.json")
    try:
        with open(json_path, 'w') as json_file:
            json.dump(presentation_details, json_file, indent=4)
    except Exception as e:
        logger.error("Error saving presentation details: %s", e)
        return jsonify({"error": "Failed to save presentation details"}), 500

    return jsonify(presentation_details), 201

@presentation_routes.route("/<presentation_id>", methods=["GET"])
def get_presentation_details(presentation_id):
    """
    Retrieves the details of a specific presentation.
    """
    json_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.json")
    if not os.path.exists(json_path):
        return jsonify({"error": "Presentation not found"}), 404

    try:
        with open(json_path, 'r') as json_file:
            presentation_details = json.load(json_file)
    except Exception as e:
        logger.error("Error reading presentation details: %s", e)
        return jsonify({"error": "Failed to read presentation details"}), 500

    return jsonify(presentation_details), 200

@presentation_routes.route("/<presentation_id>/download", methods=["GET"])
def download_presentation(presentation_id):
    """
    Allows users to download the generated PowerPoint presentation.
    """
    pptx_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.pptx")
    if os.path.exists(pptx_path):
        return send_file(pptx_path, as_attachment=True)
    return jsonify({"error": "Presentation not found"}), 404

@presentation_routes.route("/<presentation_id>/configure", methods=["POST"])
def configure_presentation(presentation_id):
    """
    Modifies the configuration of an existing presentation.
    """
    json_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.json")
    pptx_path = os.path.join(GENERATED_FILES_DIR, f"{presentation_id}.pptx")

    if not os.path.exists(json_path):
        return jsonify({"error": "Presentation not found"}), 404

    try:
        with open(json_path, 'r') as json_file:
            presentation_details = json.load(json_file)
    except Exception as e:
        logger.error("Error reading presentation details: %s", e)
        return jsonify({"error": "Failed to read presentation details"}), 500

    data = request.json

    # Update topic if provided
    if "topic" in data:
        presentation_details["topic"] = data["topic"]

    # Update number of slides if provided
    if "num_slides" in data:
        num_slides = data["num_slides"]
        if not isinstance(num_slides, int) or not (1 <= num_slides <= 20):
            return jsonify({"error": "num_slides must be an integer between 1 and 20"}), 400
        presentation_details["num_slides"] = num_slides
    else:
        num_slides = presentation_details["num_slides"]

    # Update theme if provided
    if "theme" in data:
        theme = data["theme"]
        if theme not in themes:
            return jsonify({"error": f"Unsupported theme: {theme}"}), 400
        presentation_details["theme"] = theme
    else:
        theme = presentation_details["theme"]

    # Update layouts if provided
    if "layouts" in data:
        layouts = data["layouts"]
        supported_layouts = {"title", "bullet_points", "two_column", "content_with_image"}
        if not isinstance(layouts, list):
            return jsonify({"error": "layouts must be a list"}), 400
        for layout in layouts:
            if layout not in supported_layouts:
                return jsonify({"error": f"Unsupported layout type: {layout}"}), 400
        # Ensure layouts list matches num_slides
        if len(layouts) < num_slides:
            layouts += ["bullet_points"] * (num_slides - len(layouts))
        elif len(layouts) > num_slides:
            layouts = layouts[:num_slides]
        presentation_details["layouts"] = layouts
    else:
        layouts = presentation_details["layouts"]

    # Fetch new content using Gemini
    try:
        content = fetch_content_from_gemini(presentation_details["topic"], num_slides, layouts)
        # logger.info("Updated content before creating presentation: %s", content)
    except Exception as e:
        logger.error("Error fetching updated content: %s", e)
        return jsonify({"error": str(e)}), 500

    # Create the updated presentation
    try:
        prs = create_presentation(content, theme_name=theme)
    except Exception as e:
        logger.error("Error creating updated presentation: %s", e)
        return jsonify({"error": "Failed to create updated presentation"}), 500

    # Save the updated PPTX file
    try:
        prs.save(pptx_path)
    except Exception as e:
        logger.error("Error saving updated presentation file: %s", e)
        return jsonify({"error": "Failed to save updated presentation file"}), 500

    # Update the JSON file with new details
    presentation_details["status"] = "updated"

    try:
        with open(json_path, 'w') as json_file:
            json.dump(presentation_details, json_file, indent=4)
    except Exception as e:
        logger.error("Error updating presentation details: %s", e)
        return jsonify({"error": "Failed to update presentation details"}), 500

    return jsonify(presentation_details), 200
