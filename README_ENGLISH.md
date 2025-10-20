# RAG Query Rewrite POC

A Proof of Concept demonstrating a RAG system with intelligent query rewriting capabilities. Transforms user queries to improve retrieval accuracy through expansion, decomposition, and refinement techniques. Features configurable rewrite strategies, performance metrics, and modular architecture for experimenting with query optimization approaches.

## 🌟 Features

- **Multiple Query Rewrite Strategies**
  - **Expansion**: Enhance queries with synonyms and related terms
  - **Decomposition**: Break complex queries into simpler sub-queries
  - **Refinement**: Clarify and improve query specificity
  - **Hybrid**: Combine multiple strategies for optimal results

- **Flexible Document Processing**
  - Support for PDF, TXT, DOCX, and Markdown files
  - Intelligent text chunking with configurable overlap
  - Batch document ingestion

- **Vector Store Options**
  - ChromaDB for persistent storage
  - FAISS for high-performance in-memory search
  - Easy switching between implementations

- **Production-Ready API**
  - FastAPI-based REST API
  - Interactive API documentation (Swagger UI)
  - Docker deployment support
  - Health checks and monitoring

## 📋 Prerequisites

- **Python 3.11-3.12** (recommended for full features)
  - Python 3.13 is supported but FAISS vector store is not available (ChromaDB works fine)
- OpenAI API key
- UV (recommended) or pip for package management
- Docker (optional, for containerized deployment)

> **Note for Python 3.13 users**: The `faiss-cpu` library doesn't have wheels for Python 3.13 yet. The system will automatically use ChromaDB as the vector store, which works perfectly fine. To use FAISS, please use Python 3.12 or earlier.

## 🚀 Quick Start

### Option A: Using UV (Recommended - Fast & Modern)

[UV](https://github.com/astral-sh/uv) is an extremely fast Python package installer and resolver, written in Rust.

```bash
# Install UV (if not already installed)
# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd rag-query-rewrite-poc

# Create virtual environment with UV
# For Python 3.12 (recommended for full FAISS support):
uv venv --python 3.12

# Or let UV use your default Python:
# uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies with UV (much faster than pip)
uv pip install -r requirements.txt
```

### Option B: Using Traditional pip

```bash
# Clone the repository
git clone <repository-url>
cd rag-query-rewrite-poc

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option C: Automated Setup Scripts

```bash
# On Windows (with UV):
setup-uv.bat

# On Linux/Mac (with UV):
bash setup-uv.sh

# On Windows (traditional pip):
setup.bat

# On Linux/Mac (traditional pip):
bash setup.sh
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

### 3. Run Examples

```bash
# Run interactive examples
python example.py
```

### 4. Start API Server

```bash
# Start the FastAPI server
python api.py

# API will be available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🤖 Agent Framework Integration (Optional)

The system includes **optional** support for agent-framework orchestration. This is **disabled by default** and requires separate installation.

### What is Agent Framework?

Agent Framework provides multi-agent orchestration with specialized agents:
- **QueryAnalyzer Agent**: Analyzes and rewrites queries
- **DocumentRetriever Agent**: Retrieves relevant documents  
- **AnswerGenerator Agent**: Generates answers from context

### Quick Check - Are You Using It?

**By default: NO** - You're using the standard RAG pipeline (simpler and faster).

To verify:
```bash
# Check configuration
grep ORCHESTRATION .env
# If not set or "false", you're using standard pipeline

# Check if installed
pip show agent-framework
# If "Package not found", agent framework is not installed
```

### Installation & Setup

**Step 1: Install agent-framework**
```bash
# Using pip
pip install agent-framework --pre

# Using UV (faster)
uv pip install agent-framework --pre

# Or use automated script
./install_orchestration.sh     # Linux/Mac
install_orchestration.bat      # Windows
```

**Step 2: Enable in configuration**
```bash
# Add to .env file
echo "USE_AGENT_ORCHESTRATION=true" >> .env
```

**Step 3: Restart API server**
```bash
python api.py
# You should see: "Agent orchestrator initialized successfully"
```

### Usage Examples

**In API (per-request override):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué cubre el plan de beneficios?",
    "use_orchestration": true,
    "max_queries": 3,
    "top_k": 5
  }'
```

**In Python code:**
```python
from agent_orchestrator import create_orchestrator
from rag_pipeline import create_pipeline

# Create pipeline and orchestrator
pipeline = create_pipeline(max_queries=3)
orchestrator = create_orchestrator(rag_pipeline=pipeline)

# Query with orchestration
result = orchestrator.query_with_orchestration(
    question="¿Qué incluye el plan Northwind Health Plus?",
    top_k=5,
    return_sources=True
)

print(f"Answer: {result['answer']}")
print(f"Orchestration used: {result['orchestration_used']}")
print(f"Agent results: {result['agent_results']}")
```

**Run complete examples:**
```bash
python example_orchestration.py
```

### Documentation

For detailed information about agent framework:
- **Installation Guide**: `install_orchestration.sh` / `.bat`
- **Comprehensive Docs**: `README_ORCHESTRATION.md`
- **Integration Guide**: `AGENT_FRAMEWORK_INTEGRATION.md`
- **Current State**: `CURRENT_STATE.md`
- **Example Code**: `example_orchestration.py`
- **Source Code**: `agent_orchestrator.py`

### When to Use Agent Framework

**Use Agent Framework (enable orchestration) when:**
- ✅ Need detailed agent execution tracking
- ✅ Building complex multi-agent workflows
- ✅ Experimenting with different agent configurations
- ✅ Want to scale individual components separately
- ✅ Need advanced debugging and observability

**Use Standard Pipeline (default) when:**
- ✅ Normal RAG operations (most common)
- ✅ Want faster response times
- ✅ Simpler deployment requirements
- ✅ Production systems with proven workflows
- ✅ Resource-constrained environments

### Comparison

| Feature | Standard Pipeline (Default) | Agent Orchestration (Optional) |
|---------|---------------------------|-------------------------------|
| **Installation** | Basic deps only | Requires `agent-framework --pre` |
| **Configuration** | None needed | `USE_AGENT_ORCHESTRATION=true` |
| **Current Status** | ✅ Active | ❌ Disabled |
| **Speed** | Faster | Slightly slower |
| **Complexity** | Simple | More complex |
| **Observability** | Basic logs | Agent-level tracking |
| **Use Cases** | General RAG | Advanced workflows |

### Architecture Comparison

**Standard Pipeline (What You're Currently Using):**
```
User Query → Query Rewriter → Vector Store → LLM → Answer
```

**Agent Orchestration (Optional Enhancement):**
```
User Query → Agent Orchestrator
              ├─ QueryAnalyzer Agent
              ├─ DocumentRetriever Agent  
              └─ AnswerGenerator Agent
              → Answer
```

### Quick Start with Agent Framework

```bash
# 1. Install
pip install agent-framework --pre

# 2. Enable
echo "USE_AGENT_ORCHESTRATION=true" >> .env

# 3. Test
python example_orchestration.py

# 4. Use in API
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "test", "use_orchestration": true}'
```

> **Note**: Agent framework is completely optional. Your system works perfectly with the standard pipeline (default mode). Only enable agent orchestration if you need advanced multi-agent capabilities.



## 📖 Usage Examples

### Basic Query

```python
from rag_pipeline import create_pipeline

# Create pipeline with query rewriting
pipeline = create_pipeline(enable_rewrite=True)

# Ingest documents
pipeline.ingest_documents(
    source="path/to/document.pdf",
    source_type="file"
)

# Query the system
result = pipeline.query("What is machine learning?")
print(result['answer'])
```

### Using Different Rewrite Strategies

```python
# Expansion strategy
pipeline = create_pipeline(rewrite_strategy="expansion")

# Decomposition strategy
pipeline = create_pipeline(rewrite_strategy="decomposition")

# Hybrid strategy (recommended)
pipeline = create_pipeline(rewrite_strategy="hybrid")
```

### API Usage

```bash
# Ingest a document
curl -X POST "http://localhost:8000/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document content here",
    "metadata": {"source": "example"}
  }'

# Query the system
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is RAG?",
    "top_k": 5,
    "enable_rewrite": true
  }'

# Test query rewriting
curl -X POST "http://localhost:8000/rewrite?question=What is AI?"

# Get system statistics
curl "http://localhost:8000/stats"
```

## 🏗️ Architecture

```
┌─────────────────┐
│  User Query     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Rewriter  │ ← Expansion, Decomposition, Refinement
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Vector Store    │ ← Multi-query retrieval
│ (Chroma/FAISS)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Generator   │ ← Context-aware answer generation
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final Answer   │
└─────────────────┘
```

## 📁 Project Structure

```
rag-query-rewrite-poc/
├── api.py                  # FastAPI application
├── config.py               # Configuration management
├── query_rewriter.py       # Query rewriting logic
├── vector_store.py         # Vector store implementation
├── document_processor.py   # Document loading and chunking
├── rag_pipeline.py         # Main RAG pipeline
├── example.py              # Usage examples
├── test_rag.py            # Unit tests
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── .env.example           # Example environment variables
└── README.md              # This file
```

## ⚙️ Configuration

Edit `.env` file or set environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Vector Store
VECTOR_STORE_TYPE=chroma  # or faiss
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Query Rewrite
ENABLE_QUERY_REWRITE=true
REWRITE_STRATEGY=hybrid  # expansion, decomposition, refinement, hybrid

# RAG Settings
TOP_K_RESULTS=5
TEMPERATURE=0.7
MAX_TOKENS=1000

# API Settings
API_PORT=8000
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Run unit tests
pytest test_rag.py -v

# Run with coverage
pytest test_rag.py --cov=. --cov-report=html
```

## 💡 Why UV?

UV offers several advantages over traditional pip:

- ⚡ **10-100x faster** than pip for package installation
- 🔒 **Better dependency resolution** with automatic conflict detection
- 🎯 **Compatible** with existing pip workflows and requirements.txt
- 🦀 **Written in Rust** for maximum performance
- 📦 **Drop-in replacement** - works with existing Python projects
- 🐍 **Python version management** - easily create environments with specific Python versions

Example speed comparison:
```bash
# Traditional pip install
pip install -r requirements.txt  # ~45 seconds

# UV install
uv pip install -r requirements.txt  # ~3 seconds
```

### UV Python Version Management

```bash
# Create environment with specific Python version
uv venv --python 3.12

# Or specify exact version
uv venv --python 3.12.7

# UV can even download and install Python versions for you
uv venv --python 3.12 --python-preference managed
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/query` | POST | Query the RAG system |
| `/ingest/text` | POST | Ingest raw text |
| `/ingest/file` | POST | Upload and ingest file |
| `/rewrite` | POST | Test query rewriting |
| `/stats` | GET | Get system statistics |

Full API documentation available at `http://localhost:8000/docs`

## 🔧 Advanced Features

### Custom Query Rewriting

```python
from query_rewriter import QueryRewriter

rewriter = QueryRewriter(strategy="hybrid")
result = rewriter.rewrite(
    query="How does AI work?",
    context={"conversation_history": "Previous discussion about ML"}
)
print(result['rewritten'])
```

### Batch Processing

```python
questions = [
    "What is Python?",
    "How does machine learning work?",
    "What is deep learning?"
]

results = pipeline.batch_query(questions, top_k=3)
```

### Custom Metadata Filtering

```python
# Search with metadata filters
results = vector_store.search(
    query="machine learning",
    filter_metadata={"source": "textbook.pdf"}
)
```

## 🤝 Contributing

Contributions are welcome! This is a POC project designed for experimentation and learning.

## 📝 License

MIT License - feel free to use this code for your own projects.

## 🙏 Acknowledgments

- Built with LangChain, OpenAI, FastAPI, and ChromaDB/FAISS
- Inspired by modern RAG architectures and query optimization techniques

## 📧 Contact

For questions or feedback, please open an issue in the repository.

---

**Note**: This is a Proof of Concept. For production use, consider adding:
- Authentication and authorization
- Rate limiting
- Caching layer
- Monitoring and observability
- Error handling improvements
- Database for conversation history
- Evaluation metrics and benchmarking
