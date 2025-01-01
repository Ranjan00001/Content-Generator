# Advanced Content Generation Platform

This platform is a sophisticated modular framework for automated content generation, encompassing blogs, presentations, and other media. Leveraging an agentic framework, it incorporates advanced capabilities such as memory management, dynamic workflows, and content reusability to enhance productivity and personalization.

---

## Directory Architecture

```
Content-Generator/
├──	backend/
    ├── configs/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── settings.py
    ├── data/
    │   ├── generated/
    │   └── memory/
    │       ├── session_memory.json
    │       ├── persistent_memory.json
    ├── models/
    │   ├── __init__.py
	│   ├── generative_model.py
	│   ├── other_models.py
	├── routes/
	│   ├── __init__.py
	│   ├── blog_routes.py
	│   ├── presentation_routes.py
	│   ├── chat_routes.py
	│   ├── image_routes.py
	│   ├── reel_routes.py
	│   ├── video_routes.py
	├── services/
	│   ├── __init__.py
	│   ├── blog_service.py
	│   ├── presentation_service.py
	│   ├── image_service.py
	│   ├── reel_service.py
	│   ├── video_service.py
	│   ├── utils.py
	│   ├── memory_service.py
	├── storage/presentations
	├──	utils/
	|	├──	__init__.py
	|	├──	database.py
	├── test/
	│   ├── __init__.py
	│   ├── presentation_service_test.py
	│   ├── memory_service_test.py
	├── .env
	├── app.py
	├── README.md
	├── requirements.txt
├──	frontend/
```

---

## Memory Integration Framework

### **Session Memory**

- Implemented with **Flask-Session** and stored in Redis.
- Temporarily retains session-specific data:
  - Current user queries and prompts.
  - Intermediate content drafts (e.g., blogs, presentations).
  - Transient contextual metadata (e.g., tone, topic preferences).

### **Persistent Memory**

- Maintained via a combination of **MongoDB** and **PostgreSQL**.
- Stores comprehensive user-specific data:
  - Preferences such as tone, themes, and styles.
  - Interaction logs, including past inputs and generated outputs.
  - Metadata (e.g., topics, timestamps, configuration parameters).
  - Revisions and final content versions.

### **Content Reusability Workflow**

1. **User Submission**: A new query or topic is initiated.
2. **Preliminary Filtering**:
   - Extract relevant entries based on user ID, topic, or metadata.
3. **Semantic Matching**:
   - Generate content embeddings using **Sentence Transformers** or OpenAI models.
   - Perform similarity matching via nearest-neighbor searches within the filtered set.
4. **Recommendations**:
   - Provide a ranked list of past outputs with confidence scores.
   - Enable users to refine, reuse, or initiate fresh content generation.

### **Data Storage Specifications**

#### **In Redis (Session Memory):**

- Temporary session-level data:
  - User inputs.
  - Context-specific parameters.

#### **In MongoDB (Persistent Memory):**

- Dynamic content archives:
  - Blogs, presentations, scripts, and metadata.
- Vector embeddings for reusability.
- Versioning details for iterative content improvements.

#### **In PostgreSQL (Persistent Metadata):**

- Structured metadata for analytics and retrieval:
  - User profiles.
  - Content generation logs.
  - Usage and download statistics.

---

## External Tools and Services

### **1. Redis**

- **Role**: High-performance session memory management.
- **Rationale**: Efficiently handles transient, high-speed data transactions.

### **2. MongoDB**

- **Role**: Flexible persistent memory storage.
- **Rationale**: Optimal for hierarchical, JSON-like data structures.

### **3. PostgreSQL**

- **Role**: Relational database for structured metadata.
- **Rationale**: Ensures robust data integrity and advanced querying capabilities.

### **4. Sentence Transformers/OpenAI Models**

- **Role**: Semantic representation for similarity searches.
- **Rationale**: Facilitates accurate retrieval of reusable content.

---

## Platform Features

- **Blog Authoring**: Iterative workflows for high-quality textual content.
- **Presentation Design**: Customizable slides to align with user-defined themes and preferences.
- **Reels and Video Support**: Seamless management of multimedia content.
- **Agentic Design**: Modular framework to incorporate advanced AI functionalities.
- **Memory Integration**: Robust mechanisms for contextual and persistent workflows.
- **Content Reusability**: Advanced semantic searches to suggest prior outputs.

---

## Deployment Guide

### Prerequisites

- Python 3.8 or higher.
- Install dependencies from `requirements.txt`.

### Installation Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/Ranjan00001/Content-Generator
   cd Content-Generator/backend
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables in `.env`.

### Execution

Run the Flask application:

```bash
python app.py
```

---

## Future Development

- **Real-time Analytics**: In-depth insights into content usage and performance.
- **Multilingual Support**: Extend capabilities for generating content in multiple languages.
- **Extensibility via Plugins**: Enable third-party integrations for enhanced functionalities.
