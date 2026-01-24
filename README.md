# Multi-Agent Calculator System

Learning to build multi-agent systems with LLMs step by step.

---

## Progress

### ✅ Step 1: Simple Calculator Tool

**What we built:**
- Basic calculator tool that evaluates math expressions

**File:** `calculator_tool.py`

---

### ✅ Step 2: Calculator Agent with LangChain

**What we built:**
- Agent that understands natural language questions
- Uses Gemini 2.5 Flash and LangChain
- Calls calculator_tool for math operations

**File:** `calculator_agent.py`

**Setup:**
```bash
pip install langchain langchain-google-genai
export GOOGLE_API_KEY='your-key-here'
python calculator_agent.py
```

---

### ✅ Step 3: Specialized Agents

**What we built:**
- Four specialized tools: add, subtract, multiply, divide
- Agent chooses the right tool for each operation

**File:** `specialized_agents.py`

**How to use:**
```bash
python specialized_agents.py
```

---

## Project Structure
```
Calculator_multi_agent/
├── calculator_tool.py       # Step 1: Basic calculator tool
├── calculator_agent.py      # Step 2: LangChain agent
├── specialized_agents.py    # Step 3: Specialized operation tools
└── README.md               # This file
```