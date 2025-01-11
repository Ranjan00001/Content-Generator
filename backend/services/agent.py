from phidata.search import InternetSearch
from models.gemini_model import GeminiModel

class InternetSearchAgent:
    def __init__(self, gemini_model: GeminiModel):
        self.search_tool = InternetSearch()
        self.gemini_model = gemini_model

    def search(self, query: str):
        results = self.search_tool.query(query)
        summarized_results = self.gemini_model.summarize(results)
        return summarized_results


from phidata.db import DatabaseRetriever
from models.gemini_model import GeminiModel

class DatabaseRetrieverAgent:
    def __init__(self, database_uri: str, gemini_model: GeminiModel):
        self.db_retriever = DatabaseRetriever(database_uri)
        self.gemini_model = gemini_model

    def fetch_data(self, topic: str):
        records = self.db_retriever.query(f"SELECT * FROM blogs WHERE topic LIKE '%{topic}%'")
        insights = self.gemini_model.extract_key_points(records)
        return insights


from models.gemini_model import GeminiModel

class UserInfoAgent:
    def __init__(self, gemini_model: GeminiModel):
        self.gemini_model = gemini_model

    def process_user_input(self, user_input: str):
        refined_input = self.gemini_model.refine(user_input)
        return refined_input


from agents.internet_search_agent import InternetSearchAgent
from agents.database_retriever_agent import DatabaseRetrieverAgent
from agents.user_info_agent import UserInfoAgent
from models.gemini_model import GeminiModel

def generate_blog(topic: str, user_input: str):
    gemini_model = GeminiModel()

    # Initialize agents
    internet_agent = InternetSearchAgent(gemini_model)
    database_agent = DatabaseRetrieverAgent("database_uri_here", gemini_model)
    user_info_agent = UserInfoAgent(gemini_model)

    # Gather data
    internet_data = internet_agent.search(topic)
    database_data = database_agent.fetch_data(topic)
    user_data = user_info_agent.process_user_input(user_input)

    # Combine all insights
    blog_content = f"""
    {internet_data}

    {database_data}

    {user_data}
    """
    return blog_content

if __name__ == "__main__":
    topic = input("Enter blog topic: ")
    user_input = input("Enter additional information: ")
    blog = generate_blog(topic, user_input)
    print("Generated Blog:")
    print(blog)
