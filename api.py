"""
FastAPI Backend for Multi-Tool Agent System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gemini_service import create_agent, TOOLS

app = FastAPI(title="Multi-Tool Agent API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    question: str

# Response model
class QueryResponse(BaseModel):
    answer: str
    success: bool

# Initialize agent
agent = create_agent()

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "available_tools": [t.name for t in TOOLS]
    }

@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    """
    Send a query to the agent
    
    Example:
    POST /query
    {
        "question": "What is 25 * 4?"
    }
    """
    try:
        result = agent.invoke({"input": request.question})
        return QueryResponse(
            answer=result['output'],
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools")
def list_tools():
    """List all available tools"""
    return {
        "tools": [
            {
                "name": t.name,
                "description": t.description
            }
            for t in TOOLS
        ]
    }