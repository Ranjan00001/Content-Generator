from googlesearch import search
import requests
import logging
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchAgent:

    def clean_html(self, html_content):
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


    def fetch_articles(self, query="Gen AI", num_results=3):
        """
        Fetches the latest news articles based on the query.
        """
        try:
            search_results = search(query, num_results=num_results, advanced=True)
            articles = []
            for result in search_results:
                try:
                    response = requests.get(result.url, timeout=5)
                    if response.status_code == 200:
                        body = self.clean_html(response.text)
                        if body:
                            articles.append(body)
                except:
                    logger.warning("falied to get the article from internet!")
            # for result in search_results:
            #     articles.append(result.description)
            return articles
        except Exception as e:
            logger.error(f"Error fetching latest news: {e}")
            return []