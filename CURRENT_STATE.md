# Current System State - RAG Query Rewrite

## ❓ Is Everything Using Agent Framework?

**NO** - The agent-framework integration is **OPTIONAL** and **DISABLED BY DEFAULT**.

## 🎯 Current Architecture

### **Default Behavior (What You're Using Now):**

```
User Query
    ↓
Standard RAG Pipeline
    ├─ Query Rewriter (query_rewriter.py)
    ├─ Vector Store (ChromaDB/FAISS)
    └─ LLM Generator (OpenAI)
    ↓
Answer
```

### **Optional Agent Framework (Not Active):**

```
User Query
    ↓
Agent Orchestrator (DISABLED by default)
    ├─ QueryAnalyzer Agent
    ├─ DocumentRetriever Agent
    └─ AnswerGenerator Agent
    ↓
Answer
```

## 📋 What's Currently Active?

### ✅ **Active Components:**

1. **Standard RAG Pipeline** (`rag_pipeline.py`)
   - Query rewriting with configurable strategies
   - Vector store integration (ChromaDB)
   - LLM-based answer generation
   - Max queries control (default: 3)

2. **Query Rewriter** (`query_rewriter.py`)
   - Hybrid strategy (refinement + expansion)
   - Preserves specific entities (Northwind Health, etc.)
   - Generates 3 query variations by default

3. **FastAPI Server** (`api.py`)
   - REST API endpoints
   - Interactive Swagger UI
   - Standard pipeline execution

4. **Chat UI** (`chat_ui.html`)
   - Web interface for testing
   - Max queries control
   - Query rewrite visibility toggle

### ❌ **Inactive Components (Optional):**

1. **Agent Orchestrator** (`agent_orchestrator.py`)
   - Not loaded by default
   - Requires agent-framework installation
   - Must be explicitly enabled

## 🔍 How to Check Current State

### Check Configuration:

```bash
# View your .env file
cat .env

# Look for this line:
# USE_AGENT_ORCHESTRATION=false  ← Currently DISABLED
```

### Check API Startup Logs:

```bash
python api.py

# You should see:
# "Agent orchestration disabled or not available"
# NOT: "Agent orchestrator initialized successfully"
```

### Check if agent-framework is installed:

```bash
pip show agent-framework
# If not installed, you'll see: "WARNING: Package(s) not found: agent-framework"
```

## 🎛️ Two Modes of Operation

### **Mode 1: Standard Pipeline (Current Default)**

**Status:** ✅ Active  
**Requirements:** Basic dependencies only  
**Configuration:** No special setup needed  

**How it works:**
```python
# In api.py
USE_ORCHESTRATION = False  # Default

# Queries use standard pipeline
result = pipeline.query(question, top_k, return_sources)
```

**When to use:**
- Normal operation (default)
- Simpler, faster execution
- Production deployments
- When you don't need agent tracking

---

### **Mode 2: Agent Orchestration (Optional)**

**Status:** ❌ Disabled by default  
**Requirements:** `pip install agent-framework --pre`  
**Configuration:** Set `USE_AGENT_ORCHESTRATION=true`  

**How it works:**
```python
# In api.py
USE_ORCHESTRATION = True  # Must be explicitly enabled

# Queries use agent orchestrator
result = orchestrator.query_with_orchestration(question, top_k, return_sources)
```

**When to use:**
- Need detailed agent execution tracking
- Experimenting with multi-agent workflows
- Complex query scenarios
- Building advanced orchestration patterns

## 🚦 Current System Flow

### What Happens When You Query:

```python
# 1. Request arrives at API
POST /query {"question": "¿Qué cubre el plan...?", "max_queries": 3}

# 2. API checks orchestration setting
USE_ORCHESTRATION = False  # Your current setting

# 3. Standard pipeline executes
pipeline.query()
    ├─ Query Rewriter generates 3 variations (max_queries=3)
    ├─ Vector Store searches with all 3 queries
    ├─ LLM generates answer from retrieved context
    └─ Returns response with sources

# 4. Response sent back
{"answer": "...", "sources": [...], "metadata": {...}}
```

**Agent framework is NOT involved in this flow.**

## 📊 Feature Comparison

| Feature | Standard Pipeline | Agent Orchestration |
|---------|------------------|---------------------|
| **Currently Active** | ✅ YES | ❌ NO |
| **Installation** | Basic deps only | Requires agent-framework |
| **Configuration** | Works out of box | Needs USE_AGENT_ORCHESTRATION=true |
| **Speed** | Faster | Slightly slower (orchestration overhead) |
| **Complexity** | Simple | More complex |
| **Observability** | Basic logs | Agent-level tracking |
| **Your Current Use** | ✅ Using this | ❌ Not using this |

## 🔧 How to Enable Agent Framework (If Desired)

### Step 1: Install agent-framework

```bash
pip install agent-framework --pre
# or
uv pip install agent-framework --pre
# or
./install_orchestration.sh  # Automated script
```

### Step 2: Enable in Configuration

```bash
# Edit .env file
echo "USE_AGENT_ORCHESTRATION=true" >> .env
```

### Step 3: Restart API

```bash
# Stop current API server (Ctrl+C)
python api.py

# You should now see:
# "Agent orchestrator initialized successfully"
```

### Step 4: Test with Orchestration

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "¿Qué cubre el plan?",
    "use_orchestration": true
  }'
```

## ✅ Bottom Line

### What You Have Right Now:

- ✅ **Standard RAG Pipeline** - Working perfectly
- ✅ **Query Rewriting** - Generating 3 variations
- ✅ **Entity Preservation** - Keeping "Northwind Health" intact
- ✅ **FastAPI Server** - Running at localhost:8000
- ✅ **Chat UI** - Interactive web interface
- ❌ **Agent Framework** - Not installed, not active

### What's Different:

**Before my changes:**
- Generated 7 query variations (too many)
- Generic placeholders in queries ("[Company Name]")
- No agent orchestration option

**After my changes:**
- Generates 3 query variations (configurable)
- Preserves specific entities ("Northwind Health")
- Agent orchestration available (but disabled by default)
- System still uses standard pipeline unless you enable orchestration

## 🎯 Summary

**You are NOT using agent-framework.** Your system runs on the standard RAG pipeline, which is simpler, faster, and works perfectly for most use cases. The agent-framework integration was added as an **optional enhancement** that you can enable later if needed.

**Current Setup:**
```
┌─────────────────────────────────────┐
│     Standard RAG Pipeline           │  ← You are here
│  (Fast, Simple, Production-Ready)   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│   Agent Framework Orchestration     │  ← Optional (disabled)
│     (Advanced, Experimental)        │
└─────────────────────────────────────┘
```

Everything is working with the **standard pipeline** - agent-framework is just an optional add-on for advanced scenarios.
