from models.generative_model import get_model

model = get_model()
session_state = {
    "chat": model.start_chat(history=[]),
    "revisedPrompt": ''
}

# Define the initial prompt
initial_prompt = (
    'I want you to become my prompt engineer. Your objective is to assist me in creating the most '
    'effective prompt tailored to my requirements. This prompt will be used by you. '
    'Follow these steps:\n1. In your first response, ask me what the prompt should be about. '
    'I will provide my answer, and we will improve it through continual iterations using the following steps. '
    '2. Based on my input, generate two sections:\n  a) Revised Prompt: Provide your rewritten prompt, which '
    'should be straightforward, brief, and simple to comprehend.\n  b) Questions: Ask any relevant questions '
    'to gather additional information needed to improve the prompt.\n3. We will continue this iterative process, '
    'with me providing additional information and you updating the prompt in the Revised Prompt section, until I confirm we are done.'
)

# Utility functions
def get_response_text(response):
    try:
        return response['candidates'][0]['content']['parts'][0]['text']
    except (IndexError, KeyError):
        return "No response available from the model."

def extract_revised_prompt(response_text):
    start_marker = "Revised Prompt:"
    end_marker = "Questions:"
    start = response_text.find(start_marker) + len(start_marker)
    end = response_text.find(end_marker, start)
    if start != -1 and end != -1:
        return response_text[start:end].strip('*\n()')
    return "Revised prompt not found."
