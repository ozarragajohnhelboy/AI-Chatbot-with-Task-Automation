# AI Chatbot with Task Automation

Enterprise-grade AI chatbot powered by TensorFlow and LangChain with intelligent task automation capabilities.

## Features

- **Natural Language Understanding**: TensorFlow-based intent classification and entity extraction
- **Task Automation**: Execute file operations, schedule reminders, run scripts via natural language
- **Conversational Memory**: Context-aware conversations with learning capabilities
- **Modern API**: FastAPI backend with async support
- **Extensible Architecture**: Clean, modular design following SOLID principles

## Tech Stack

- **ML/AI**: TensorFlow 2.15, LangChain, Transformers, Sentence-Transformers
- **Backend**: FastAPI, Uvicorn
- **Task Queue**: Celery, Redis, APScheduler
- **Vector Store**: ChromaDB
- **NLP**: OpenAI GPT (optional), Custom TensorFlow models

## Project Structure

```
tf_project/
├── app/
│   ├── api/              # FastAPI routes
│   ├── core/             # Core configs
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   └── main.py           # App entry point
├── ml/
│   ├── intent/           # Intent classification
│   ├── entity/           # Entity extraction
│   ├── training/         # Model training scripts
│   └── inference/        # Model inference
├── automation/
│   ├── tasks/            # Task executors
│   ├── scheduler/        # Task scheduling
│   └── handlers/         # Command handlers
├── memory/
│   ├── conversation/     # Conversation storage
│   ├── vector_store/     # Semantic search
│   └── learning/         # Continuous learning
├── data/                 # Data storage
├── frontend/             # Web UI
└── tests/               # Test suite
```

## Quick Start

### Installation

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

```bash
cp .env.example .env
```

Edit `.env` with your configuration.

### Run Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Train Models

```bash
python ml/training/train_intent_classifier.py
```

## API Endpoints

- `POST /api/v1/chat` - Send message to chatbot
- `GET /api/v1/conversations` - Get conversation history
- `POST /api/v1/tasks` - Execute automated task
- `GET /api/v1/tasks/{task_id}` - Get task status
- `POST /api/v1/learn` - Teach chatbot from feedback

## Development

Built with production-grade practices:
- Clean architecture
- Type hints throughout
- Async/await patterns
- Dependency injection
- Comprehensive error handling

## License

MIT

