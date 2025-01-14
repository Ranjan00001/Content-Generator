import logging
from datetime import datetime
from flask import jsonify
from transformers import BertTokenizer, BertModel
import torch.nn.functional as F
import torch
from models.generative_model import (
    get_model,
    extract_revised_prompt_and_questions,
    ModelResponseKeys,
    format_model_response,
    getBlogGenerationPrompt,
)
from services.memory_service import MemoryAgent
from services.search_service import SearchAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BlogService:
    def __init__(self):
        self.tokenizer = BertTokenizer.from_pretrained('bert-large-uncased')
        self.embedding_model = BertModel.from_pretrained('bert-large-uncased')
        self.model = get_model()
        self.memory_service = MemoryAgent()
        self.session_state = {
            "chat": self.model.start_chat(history=[]),
            "revisedPrompt": ''
        }
        self.initial_prompt = (
            'I want you to become my prompt engineer. Your objective is to assist me in creating the most '
            'effective prompt tailored to my requirements. This prompt will be used by you. '
            'Follow these steps:\n1. In your first response, ask me what the prompt should be about. '
            'I will provide my answer, and we will improve it through continual iterations using the following steps. '
            '2. Based on my input, generate two sections:\n  a) Revised Prompt: Provide your rewritten prompt, which '
            'should be straightforward, brief, and simple to comprehend.\n  b) Questions: Ask any relevant questions '
            'to gather additional information needed to improve the prompt.\n3. We will continue this iterative process, '
            'with me providing additional information and you updating the prompt in the Revised Prompt section, until I confirm we are done.'
        )

    def get_response_text(self, response):
        try:
            return response['candidates'][0]['content']['parts'][0]['text']
        except (IndexError, KeyError):
            return "No response available from the model."

    def extract_revised_prompt(self, response_text):
        start_marker = "Revised Prompt:"
        end_marker = "Questions:"
        start = response_text.find(start_marker) + len(start_marker)
        end = response_text.find(end_marker, start)
        if start != -1 and end != -1:
            return response_text[start:end].strip('*\n()')
        return "Revised prompt not found."

    def refine_prompt(self, user_query):
        if user_query.lower() == "done":
            final_prompt = self.session_state['revisedPrompt']
            try:
                final_response = self.model.generate_content(final_prompt).to_dict()
                final_text = self.get_response_text(final_response)
                inputs = self.tokenizer(
                    final_text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )

                with torch.no_grad():
                    outputs = self.embedding_model(**inputs)
                embedding = torch.mean(outputs.last_hidden_state, dim=1).squeeze().tolist()

                mongo_id = self.memory_service.store_content_in_mongo(
                    user_id="user123",
                    content_type="blog",
                    content={"revised_prompt": final_text},
                    additional_info={"status": "generated"}
                )
                self.memory_service.store_vector_embedding(
                    user_id="user123",
                    mongo_doc_id=mongo_id,
                    embedding=embedding,
                    content_type="blog",
                    additional_info="tone: conversational",
                    # created_at=datetime.now()
                )
                logger.info(f"Generated blog content stored in MongoDB with ID: {mongo_id}")
                return jsonify({'Final Blog': final_text}), 200
            except Exception as e:
                logger.error(f"Error generating final content: {e}")
                return jsonify({"error": "Failed to generate final content."}), 500

        try:
            response = self.session_state["chat"].send_message(user_query)
            response_text = self.get_response_text(response.to_dict())
            revised_prompt, questions = extract_revised_prompt_and_questions(response_text)
            self.session_state['revisedPrompt'] = revised_prompt
            return jsonify(format_model_response(revised_prompt, questions)), 200
        except Exception as e:
            logger.error(f"Error refining prompt: {e}")
            return jsonify({"error": "Failed to refine prompt."}), 500

class BlogService2:
    def __init__(self):
        """
        Initialize BlogServices with a database handler and Gemini model.
        """
        self.memory_service = MemoryAgent()
        self.search_service = SearchAgent()

    def getPreviousContents(self, query):
        tokenizer = BertTokenizer.from_pretrained('bert-large-uncased')
        embedding_model = BertModel.from_pretrained('bert-large-uncased')
        inputs = tokenizer(
                    query,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
        )

        with torch.no_grad():
            outputs = embedding_model(**inputs)
        query_embedding = torch.mean(outputs.last_hidden_state, dim=1).squeeze().tolist()

        embeddings = self.memory_service.query_embeddings(user_id="user123", content_type="blog")

        nearest_embeddings = sorted(
            embeddings,
            key=lambda x: F.cosine_similarity(
            torch.tensor(query_embedding, dtype=torch.float32).unsqueeze(0),
            torch.tensor(x.embedding, dtype=torch.float32).unsqueeze(0)
            ).item(), reverse=True
        )[:5]

        results = []
        for e in nearest_embeddings:
            mongo_doc = self.memory_service.query_content_from_mongo(e.mongo_doc_id)
            if mongo_doc:
                results.append({"id": e.mongo_doc_id, "content": mongo_doc.get("content")})

        return results

    def get_response_text(self, response):
        try:
            return response['candidates'][0]['content']['parts'][0]['text']
        except (IndexError, KeyError):
            return "No response available from the model."

    def generateBlog(self, query):
        a = self.getPreviousContents(query)
        b = self.search_service.fetch_articles(query)
        print(a, b)
        final_prompt = getBlogGenerationPrompt(query, a, b)
        final_response = get_model().generate_content(final_prompt).to_dict()
        final_text = self.get_response_text(final_response)

        return final_text