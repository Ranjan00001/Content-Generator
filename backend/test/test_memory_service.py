from services.memory_service import MemoryService

# Test storing content in MongoDB
mongo_id = MemoryService.store_content_in_mongo(
    user_id="user123",
    content_type="blog",
    content="This is a sample blog.",
    additional_info={"tone": "conversational", "keywords": ["AI", "technology"]}
)

# Test storing vector embedding in PostgreSQL
MemoryService.store_vector_embedding(
    user_id="user123",
    mongo_doc_id=mongo_id,
    embedding=[0.1, 0.2, 0.3, 0.4],
    content_type="blog",
    additional_info="tone: conversational"
)

# Query vector embeddings
embeddings = MemoryService.query_embeddings(user_id="user123", content_type="blog")
for embedding in embeddings:
    print(f"Embedding ID: {embedding.id}, MongoDB Doc ID: {embedding.mongo_doc_id}, Info: {embedding.additional_info}")

# Store an action log
if embeddings:
    MemoryService.store_action_log(
        embedding_id=embeddings[0].id,
        action_type="generated",
        details="Initial blog vector embedding created."
    )

# Query content from MongoDB
content = MemoryService.query_content_from_mongo(mongo_id)
print(f"Content: {content['content']}, Additional Info: {content['additional_info']}")
