from flask import jsonify, request, Blueprint
from services.chat_service import (
    session_state,
    get_response_text,
    initial_prompt,
    extract_revised_prompt,
    model,
)
from models.generative_model import extract_revised_prompt_and_questions, ModelResponseKeys, format_model_response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blog_routes = Blueprint("blog_routes", __name__)

@blog_routes.route('/initial', methods=['GET'])
def generate_initial_prompt():
    """
    API route to generate the initial prompt for the blog.
    """
    try:
        response = session_state["chat"].send_message(initial_prompt)
        response_text = get_response_text(response.to_dict())

        # Extract revised prompt and questions
        revised_prompt, questions = extract_revised_prompt_and_questions(response_text)

        # Store the revised prompt in the session state
        session_state[ModelResponseKeys.REVISED_PROMPT.value] = revised_prompt

        # Return the structured response
        return jsonify(format_model_response(revised_prompt, questions)), 200
    except Exception as e:
        logger.error(f"Error generating initial prompt: {e}")
        return jsonify({"error": "Failed to generate initial prompt."}), 500

@blog_routes.route('/refine', methods=['POST'])
def refine_prompt():
    """
    API route to refine the blog prompt based on user feedback.
    """
    data = request.json
    user_feedback = data.get("feedback", "").strip()

    if user_feedback.lower() == "done":
        final_prompt = session_state['revisedPrompt']
        # refined_prompt, questions = extract_revised_prompt_and_questions(final_prompt)
        print(final_prompt)
        try:
            final_response = model.generate_content(final_prompt).to_dict()
            final_text = get_response_text(final_response)
            return jsonify({'Final Blog': final_text}), 200
        except Exception as e:
            logger.error(f"Error generating final content: {e}")
            return jsonify({"error": "Failed to generate final content."}), 500

    try:
        response = session_state["chat"].send_message(user_feedback)
        response_text = get_response_text(response.to_dict())

        # Extract revised prompt and questions
        revised_prompt, questions = extract_revised_prompt_and_questions(response_text)

        # Update session state
        session_state['revisedPrompt'] = revised_prompt

        # Return the structured response
        return jsonify(format_model_response(revised_prompt, questions)), 200
    except Exception as e:
        logger.error(f"Error refining prompt: {e}")
        return jsonify({"error": "Failed to refine prompt."}), 500
