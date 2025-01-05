from flask import jsonify, request, Blueprint
from services.blog_service import BlogService
from models.generative_model import extract_revised_prompt_and_questions, ModelResponseKeys, format_model_response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlogController:
    def __init__(self):
        self.blueprint = Blueprint("blog_routes", __name__)
        self.blueprint.add_url_rule("/initial", view_func=self.generate_initial_prompt, methods=["GET"])
        self.blueprint.add_url_rule("/refine", view_func=self.refine_prompt, methods=["POST"])
        self.blog_service = BlogService()
        
    def generate_initial_prompt(self):
        """
        API route to generate the initial prompt for the blog.
        """
        try:
            response = self.blog_service.session_state["chat"].send_message(self.blog_service.initial_prompt)
            response_text = self.blog_service.get_response_text(response.to_dict())
            revised_prompt, questions = extract_revised_prompt_and_questions(response_text)
            self.blog_service.session_state['revisedPrompt'] = revised_prompt
            return jsonify(format_model_response(revised_prompt, questions)), 200
        except Exception as e:
            logger.error(f"Error generating initial prompt: {e}")
            return jsonify({"error": "Failed to generate initial prompt."}), 500

    def refine_prompt(self):
        """
        API route to refine the blog prompt based on user feedback.
        """
        data = request.json
        user_query = data.get("query", "").strip()
        return self.refine_prompt_helper(user_query)
    
    def refine_prompt_helper(self, user_query):
        # user_query = data.get("feedback", "").strip()

        if user_query.lower() == "done":
            final_prompt = self.blog_service.session_state['revisedPrompt']
            try:
                final_response = self.blog_service.model.generate_content(final_prompt).to_dict()
                final_text = self.blog_service.get_response_text(final_response)
                return jsonify({'Final Blog': final_text}), 200
            except Exception as e:
                logger.error(f"Error generating final content: {e}")
                return jsonify({"error": "Failed to generate final content."}), 500

        try:
            response = self.blog_service.session_state["chat"].send_message(user_query)
            response_text = self.blog_service.get_response_text(response.to_dict())
            # print(response_text)
            # Extract revised prompt and questions
            revised_prompt, questions = extract_revised_prompt_and_questions(response_text)

            # Update session state
            self.blog_service.session_state['revisedPrompt'] = revised_prompt
            # Return the structured response
            return jsonify(format_model_response(revised_prompt, questions)), 200
        except Exception as e:
            logger.error(f"Error refining prompt: {e}")
            return jsonify({"error": "Failed to refine prompt."}), 500

blog_controller = BlogController()
blog_routes = blog_controller.blueprint