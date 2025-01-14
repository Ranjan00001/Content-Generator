from flask import Blueprint, request, jsonify
import torch
import torch.nn.functional as F
from transformers import BertTokenizer, BertModel
# from datetime import datetime

from services.memory_service import MemoryAgent
from models.generative_model import get_model, reason_out_intent, Intent
# from models.generative_model import extract_revised_prompt_and_questions, ModelResponseKeys, format_model_response
from services.blog_service import BlogService, BlogService2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tokenizer = BertTokenizer.from_pretrained('bert-large-uncased')
embedding_model = BertModel.from_pretrained('bert-large-uncased')

class ChatController:
    def __init__(self):
        self.blueprint = Blueprint("chat_routes", __name__)
        self.blueprint.add_url_rule("/", view_func=self.chat, methods=["POST"])
        self.blueprint.add_url_rule("/store", view_func=self._store_in_memory, methods=["POST"])
        self.blueprint.add_url_rule("/test", view_func=self.testBlog, methods=["POST"])
        self.memory_service = MemoryAgent()
        self.blog_service = BlogService()  # Initialize BlogController

    def chat(self):
        data = request.json
        user_query = data.get("query", "").strip()
        user_feedback = data.get("feedback", None)  # Track user feedback
        prompt_refinement = data.get('refinement', False)
        intent = data.get('intent', None)
        if not user_query:
            return jsonify({"error": "Query is required"}), 400

        try:
            if not intent:
                intent_result = reason_out_intent(get_model(), user_query)
                intent = intent_result.get("intent")

            if intent == Intent.BLOG_GENERATION.value:
                query_embedding = self._generate_embedding(user_query)

                if not user_feedback:
                    embeddings = self.memory_service.query_embeddings(user_id="user123", content_type="blog")

                    nearest_embeddings = sorted(
                        embeddings,
                        key=lambda x: F.cosine_similarity(
                            torch.tensor(query_embedding, dtype=torch.float32).unsqueeze(0),
                            torch.tensor(x.embedding, dtype=torch.float32).unsqueeze(0)
                        ).item(),
                        reverse=True  # Higher similarity first
                    )[:5]
                    results = []
                    for e in nearest_embeddings:
                        mongo_doc = self.memory_service.query_content_from_mongo(e.mongo_doc_id)
                        if mongo_doc:
                            results.append({"id": e.mongo_doc_id, "content": mongo_doc.get("content")})

                    return jsonify({"intent": intent, "results": results}), 200

                elif user_feedback.lower() == "not_satisfied_with_previous_results":
                    if not prompt_refinement:
                        self.blog_service.session_state["chat"].send_message(self.blog_service.initial_prompt)
                    return self.blog_service.refine_prompt(user_query)

            elif intent == Intent.PRESENTATION_GENERATION.value:
                return jsonify({"intent": intent, "message": "Presentation generation not yet implemented."}), 501

            else:
                return jsonify({"intent": Intent.UNKNOWN.value, "message": "Unknown intent"}), 400

        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            return jsonify({"error": "Failed to process query"}), 500

    def _generate_embedding(self, text):
        """
        Generates an embedding for the given text using a model.
        """
        try:
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=4096)

            # Forward pass through the model
            with torch.no_grad():
                outputs = embedding_model(**inputs)
            return torch.mean(outputs.last_hidden_state, dim=1).squeeze().tolist()  # 1024 length embeddings

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def _store_in_memory(self):
        data = request.json
        text = data.get("Final Blog", "").strip()
        embedding = self._generate_embedding(text)
        mongo_id = self.memory_service.store_content_in_mongo(
                    user_id="user123",
                    content_type="blog",
                    content={"revised_prompt": text},
                    additional_info={"status": "generated"}
                )
        self.memory_service.store_vector_embedding(
                    user_id="user123",
                    mongo_doc_id=mongo_id,
                    embedding=embedding,
                    content_type="blog",
                    additional_info="tone: conversational",
                )
        logger.info(f"Generated blog content stored in MongoDB with ID: {mongo_id}")    
        return jsonify({'message':f"stored in database successfully, blog content stored in MongoDB with ID: {mongo_id}"}), 200

    def testBlog(self):
        data = request.json
        query = data.get('query', '')
        res = b.generateBlog(query)
        return jsonify({"result":res}), 200

b = BlogService2()
chat_controller = ChatController()
chat_routes = chat_controller.blueprint
