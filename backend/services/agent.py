# import os
# from phi.agent import Agent
# from phi.tools.googlesearch import GoogleSearch
# # from phi.db import DatabaseRetriever
# from dotenv import load_dotenv
# from phi.model.google import Gemini

# load_dotenv()
# GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')

# agent = Agent(
#     tools=[GoogleSearch()],
#     description="You are a news agent that helps users find the latest news.",
#     model=Gemini(id="gemini-1.5-flash", api_key=GOOGLE_API_KEY),
#     instructions=[
#         "Given a topic by the user, respond with all the latest news items about that topic.",
#         "Search in English and in Hindi.",
#     ],
#     show_tool_calls=True,
#     debug_mode=True,
# )


# # if __name__ == "__main__":
# agent.print_response("Kumbh Mela", markdown=True)

from googlesearch import search
import requests
from bs4 import BeautifulSoup

def clean_html(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove <script> and <style> tags
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    
    # Remove unnecessary tags (e.g., comments, metadata)
    for unwanted in soup(['noscript', 'iframe', 'svg', 'form', 'input']):
        unwanted.decompose()

    # Extract the main content (adjust selectors based on your needs)
    main_content = soup.find('body')  # Use a more specific selector if needed
    if main_content:
        # Remove empty tags and clean text
        for tag in main_content.find_all():
            if not tag.text.strip():
                tag.decompose()

    # Get cleaned text
    cleaned_text = main_content.get_text(separator=' ', strip=True) if main_content else ''
    
    return cleaned_text

query = "Give me latest information in Kumbh Mela"
results = search(query, num_results=2, advanced=True)

# for result in results:
#     print(result.description)
    # print(result.__dict__)

articles = []
for result in results:
    # print(result)
    response = requests.get(result.url, timeout=1)
    if response.status_code == 200:
        # soup = BeautifulSoup(response.text, 'html.parser')
        body = clean_html(response.text)
        if body:
            articles.append(body)
    else:
        print('error')

print(articles)