# Multi-Tool AI Agent with Memory

AI assistant powered by Google Gemini with multiple tools and semantic memory.

## Features

### Available Tools
- Calculator
- Weather
- Wikipedia Search
- Google Search
- Web Scraper
- Email
- Text Summarizer
- Memory System (semantic search with ChromaDB)

## Installation

```bash
pip install langchain langchain-google-genai chromadb wikipedia googlesearch-python beautifulsoup4 requests python-dotenv fastapi uvicorn
```

Create `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
GOOGLE_SEARCH_API_KEY=your_search_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

## Usage

### Command Line
```bash
python main.py
```

### API Server
```bash
uvicorn api:app --reload
```

API Documentation: http://localhost:8000/docs

## Project Structure

```
CALCULATOR_MULTI_AGENT/
├── chroma_memory/          # Memory database
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── .gitignore             
├── api.py                  # FastAPI server
├── gemini_service.py       # Agent configuration
├── main.py                 # Command-line interface
├── tools.py                # All tools including memory
└── README.md
```