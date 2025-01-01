import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from utils.database import VectorEmbedding, ActionLog
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB Initialization
MONGO_URI = os.getenv("MONGODB_URI")
MONGO_DB_NAME = os.getenv("MONGODB_NAME")
MONGO_COLLECTION = os.getenv("MONGODB_COLLECTION")

if not all([MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION]):
    logger.error("MongoDB configuration is incomplete. Please check environment variables.")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]
content_collection = mongo_db[MONGO_COLLECTION]

# SQLAlchemy Session
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class MemoryService:
    @staticmethod
    def store_content_in_mongo(user_id, content_type, content, additional_info):
        """Store content in MongoDB and return its ID."""
        try:
            document = {
                "user_id": user_id,
                "content_type": content_type,
                "content": content,
                "additional_info": additional_info,
                "created_at": datetime.now()
            }
            result = content_collection.insert_one(document)
            logger.info(f"Stored content in MongoDB with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error storing content in MongoDB: {e}")
            raise

    @staticmethod
    def store_vector_embedding(user_id, mongo_doc_id, embedding, content_type, additional_info):
        """Store vector embedding and link it to MongoDB content."""
        session = Session()
        try:
            new_embedding = VectorEmbedding(
                user_id=user_id,
                mongo_doc_id=mongo_doc_id,
                embedding=embedding,
                content_type=content_type,
                additional_info=additional_info,
                created_at=datetime.now()
            )
            session.add(new_embedding)
            session.commit()
            logger.info(f"Stored vector embedding for MongoDB document ID: {mongo_doc_id}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"SQLAlchemy error storing vector embedding: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error storing vector embedding: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def query_embeddings(user_id, content_type):
        """Query embeddings by user_id and content_type."""
        session = Session()
        try:
            results = session.query(VectorEmbedding).filter_by(user_id=user_id, content_type=content_type).all()
            logger.info(f"Retrieved {len(results)} embeddings for user ID: {user_id}")
            return results
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error querying embeddings: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error querying embeddings: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def store_action_log(embedding_id, action_type, details):
        """Store user action log."""
        session = Session()
        try:
            new_action_log = ActionLog(
                embedding_id=embedding_id,
                action_type=action_type,
                details=details,
                timestamp=datetime.utcnow()
            )
            session.add(new_action_log)
            session.commit()
            logger.info(f"Stored action log for embedding ID: {embedding_id}")
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"SQLAlchemy error storing action log: {e}")
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected error storing action log: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def query_content_from_mongo(mongo_doc_id):
        """Retrieve content from MongoDB using its document ID."""
        try:
            content = content_collection.find_one({"_id": ObjectId(mongo_doc_id)})  # Convert to ObjectId
            if content:
                logger.info(f"Retrieved content from MongoDB with ID: {mongo_doc_id}")
                return content
            else:
                logger.warning(f"No content found in MongoDB for ID: {mongo_doc_id}")
                return
        except Exception as e:
            logger.error(f"Error querying content from MongoDB: {e}")
            raise
