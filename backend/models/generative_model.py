import google.generativeai as genai
from enum import Enum
from dotenv import load_dotenv
import os
from configs.config import supported_layouts

load_dotenv()
# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

class SlideLayout(Enum):
    TITLE = "title"
    BULLET_POINTS = "bullet_points"
    TWO_COLUMN = "two_column"
    CONTENT_WITH_IMAGE = "content_with_image"

class ModelResponseKeys(Enum):
    """Enum for standard response structure."""
    REVISED_PROMPT = "revised_prompt"
    QUESTIONS = "questions"

# Singleton generative model instance
model = genai.GenerativeModel('gemini-1.5-flash')

def get_model():
    """Returns the generative model instance."""
    return model

def format_model_response(revised_prompt: str, questions: str) -> dict:
    """
    Formats the model's response into the standard structure.

    Args:
        revised_prompt (str): The revised prompt generated by the model.
        questions (str): Relevant questions generated by the model.

    Returns:
        dict: Structured response containing the revised prompt and questions.
    """
    return {
        ModelResponseKeys.REVISED_PROMPT.value: revised_prompt,
        ModelResponseKeys.QUESTIONS.value: questions,
    }

def extract_revised_prompt_and_questions(response_text):
    """
    Extracts the revised prompt and questions from the model's response.

    Args:
        response_text (str): The response text generated by the model.

    Returns:
        tuple: A tuple containing the revised prompt and the list of questions.
    """
    start_marker_prompt = "Revised Prompt:"
    start_marker_questions = "Questions:"

    # Extract the revised prompt
    prompt_start = response_text.find(start_marker_prompt) + len(start_marker_prompt)
    questions_start = response_text.find(start_marker_questions)
    revised_prompt = response_text[prompt_start:questions_start].strip() if questions_start != -1 else ""

    # Extract the questions
    questions_text = response_text[questions_start + len(start_marker_questions):].strip() if questions_start != -1 else ""
    questions = [q.strip("* ").strip() for q in questions_text.split("\n") if q.strip().startswith("*")]

    return revised_prompt, questions

def generate_slide_prompts(topic, num_slides, layouts):
    """
    Generates prompts for the slides based on the topic, number of slides, and layouts.

    Args:
        topic (str): The topic for the slides.
        num_slides (int): Number of slides to generate.
        layouts (list[SlideLayout]): List of slide layouts.

    Returns:
        str: Formatted prompt for the model.
    """
    prompt = f"Generate {num_slides} slides on the topic '{topic}'. Use fixed JSON keys for response: title, subtitle, points, left_points, right_points, content, and image_path. Each slide must follow the provided layout type."

    for i in range(num_slides):
        slide_num = i + 1
        layout = layouts[i] # Enum ensures valid layout values
        prompt += f"\n## Slide {slide_num}: Layout: {layout}\n"
        prompt += "Title: <Slide Title>\n"
        if layout == SlideLayout.TITLE:
            prompt += "Subtitle: <Slide Subtitle>\n"
        elif layout == SlideLayout.BULLET_POINTS:
            prompt += "Points: [\"Point 1\", \"Point 2\", \"Point 3\"]\n"
        elif layout == SlideLayout.TWO_COLUMN:
            prompt += "Left Points: [\"Left Point 1\", \"Left Point 2\"]\n"
            prompt += "Right Points: [\"Right Point 1\", \"Right Point 2\"]\n"
        elif layout == SlideLayout.CONTENT_WITH_IMAGE:
            prompt += "Content: [\"Text line 1\", \"Text line 2\"]\n"
            prompt += "Image Path: \"<Image Placeholder>\"\n"

    prompt += "\nEnsure all keys are included and the content is concise and relevant."
    return prompt
