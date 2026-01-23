# Multi-Agent Calculator System

Learning to build multi-agent systems with LLMs step by step.

---

## Progress

### ✅ Step 1: Simple Calculator Tool

**What we built:**
- A basic calculator tool that does simple math

**File:** `calculator_tool.py`

**How to use:**
```bash
python calculator_tool.py
```

---

### ✅ Step 2: LLM Agent with Gemini 3 Pro

**What we built:**
- Added Gemini 3 Pro to understand natural language
- Agent analyzes questions and decides when to use calculator tool
- Converts natural language to math expressions
- Example: "What is 25 times 4?" → extracts "25 * 4" → returns 100

**File:** `calculator_agent.py`

**Setup:**
```bash
# Install Google SDK
pip install google-generativeai

# Get API key from https://aistudio.google.com/apikey
export GOOGLE_API_KEY='your-key-here'

# Run the agent
python calculator_agent.py
```

**How it works:**
1. User asks in natural language
2. Gemini 3 Pro analyzes the question
3. Decides if it's math or not (returns JSON)
4. If math, extracts expression and calls calculator_tool
5. Returns result to user

---

## Project Structure
```
Calculator_multi_agent/
├── calculator_tool.py    # Step 1: Basic calculator tool
├── calculator_agent.py   # Step 2: LLM agent using Gemini 3 Pro
└── README.md            # This file
```
