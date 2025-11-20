"""
FastAPI backend for ICP Analysis Chat Agent.

Provides endpoints for:
- CSV file upload (enrichment data)
- Chat interactions for data analysis
- Database queries and insights
"""

import os
import json
import tempfile
import math
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

from src.config import config
from src.database import get_database_connection
from src.llm_client import LLMClient, get_default_client
from src.icp_analyzer import ICPAnalyzer
from src.data_processing import DataCleaner, SchemaMapper

# Initialize FastAPI app
app = FastAPI(
    title="ICP Analysis Agent API",
    description="Chat-based data analysis agent for ICP matching",
    version="1.0.0"
)

# CORS middleware - allow frontend to connect
# In development, allow all localhost origins
# In production, use FRONTEND_URL or allow Render origins
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# Add production origin if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)
    # Also add without trailing slash if present
    if frontend_url.endswith("/"):
        allowed_origins.append(frontend_url.rstrip("/"))
    # Also add with trailing slash if not present
    else:
        allowed_origins.append(f"{frontend_url}/")

# Allow Render preview URLs (for preview deployments)
# Format: https://icp-analysis-frontend-*.onrender.com
render_origin = os.getenv("RENDER_EXTERNAL_URL")
if render_origin:
    allowed_origins.append(render_origin)

# For development, allow all origins if DEBUG_MODE is set
# WARNING: Only use in development, not production!
debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

# In production on Render, allow all Render origins as fallback
# This ensures CORS works even if FRONTEND_URL isn't set
# (Ideally FRONTEND_URL should be set explicitly for better security)
is_render = os.getenv("RENDER") is not None

app.add_middleware(
    CORSMiddleware,
    # Use regex to allow all Render origins if on Render platform
    allow_origin_regex=r"https://.*\.onrender\.com" if (is_render and not debug_mode) else None,
    allow_origins=["*"] if debug_mode else allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Explicit OPTIONS handler for all routes (helps with some browsers)
@app.options("/{full_path:path}")
async def options_handler(full_path: str, request: Request):
    """Handle CORS preflight requests explicitly."""
    from fastapi.responses import Response
    origin = request.headers.get("origin")
    
    # Determine allowed origin
    if debug_mode:
        allow_origin = "*"
    elif origin and (origin in allowed_origins or (is_render and ".onrender.com" in origin)):
        allow_origin = origin
    elif allowed_origins:
        allow_origin = allowed_origins[0]
    else:
        allow_origin = "*"
    
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": allow_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "3600",
        }
    )

# In-memory storage for uploaded files and conversation state
# In production, use Redis or database
class AppState:
    """Application state management."""
    def __init__(self):
        self.enrichment_data: Optional[pd.DataFrame] = None
        self.signup_data: Optional[pd.DataFrame] = None
        self.analysis_result: Optional[Any] = None
        self.conversation_history: List[Dict[str, str]] = []
        self.llm_client: Optional[LLMClient] = None
    
    def reset(self):
        """Reset all state."""
        self.enrichment_data = None
        self.signup_data = None
        self.analysis_result = None
        self.conversation_history = []

# Global state instance
state = AppState()


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize data structure to ensure JSON compliance.
    Handles NaN, inf, -inf, and other problematic values.
    """
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        # Check if value is too large for JSON
        if abs(obj) > 1e308:
            return None
        return float(obj)
    elif isinstance(obj, (int, np.integer)):
        # Check if value is too large for JSON
        if abs(obj) > 2**53:  # JSON safe integer limit
            return str(obj)  # Convert to string if too large
        return int(obj)
    elif pd.isna(obj):
        return None
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    else:
        return obj


# Pydantic models for API
class ChatMessage(BaseModel):
    """Chat message from user."""
    message: str
    include_sql: bool = True


class ChatResponse(BaseModel):
    """Response from chat agent."""
    content: str
    table: Optional[Dict[str, Any]] = None
    charts: Optional[List[Dict[str, Any]]] = None
    sql: Optional[str] = None


class DataStatus(BaseModel):
    """Status of loaded data."""
    enrichment_loaded: bool
    enrichment_rows: int = 0
    enrichment_columns: int = 0
    signup_loaded: bool
    signup_rows: int = 0
    signup_columns: int = 0
    database_connected: bool = False


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ICP Analysis Agent API",
        "version": "1.0.0"
    }




@app.get("/api/status")
async def get_status() -> DataStatus:
    """Get current data status."""
    db = get_database_connection()
    db_connected, _ = db.test_connection()
    
    return DataStatus(
        enrichment_loaded=state.enrichment_data is not None,
        enrichment_rows=len(state.enrichment_data) if state.enrichment_data is not None else 0,
        enrichment_columns=len(state.enrichment_data.columns) if state.enrichment_data is not None else 0,
        signup_loaded=state.signup_data is not None,
        signup_rows=len(state.signup_data) if state.signup_data is not None else 0,
        signup_columns=len(state.signup_data.columns) if state.signup_data is not None else 0,
        database_connected=db_connected
    )


@app.post("/api/upload")
async def upload_enrichment_data(file: UploadFile = File(...)):
    """
    Upload enrichment CSV file.
    
    Args:
        file: CSV file containing enrichment data
        
    Returns:
        Success message with file info
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        # Read CSV content
        content = await file.read()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        # Load into pandas
        df = pd.read_csv(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Store in state
        state.enrichment_data = df
        
        # Get basic stats
        # Clean sample data to handle NaN/inf values for JSON serialization
        sample_df = df.head(3).copy()
        
        # Convert to dict first, then sanitize
        sample_records = sample_df.to_dict(orient='records')
        
        # Sanitize all values to ensure JSON compliance
        sanitized_sample = sanitize_for_json(sample_records)
        
        stats = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "sample": sanitized_sample
        }
        
        return {
            "status": "success",
            "message": f"Successfully uploaded {file.filename}",
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@app.post("/api/chat")
async def chat(message: ChatMessage) -> ChatResponse:
    """
    Process chat message and return analysis.
    
    Args:
        message: User's chat message
        
    Returns:
        Chat response with analysis results
    """
    try:
        # Initialize LLM client if not already done
        if state.llm_client is None:
            state.llm_client = get_default_client()
        
        # Check if data is loaded
        if state.enrichment_data is None:
            return ChatResponse(
                content="Please upload an enrichment CSV file first. Click the upload button to get started."
            )
        
        # Load signup data from database if not already loaded
        if state.signup_data is None:
            db = get_database_connection()
            success, _ = db.test_connection()
            
            if success:
                tables = db.get_tables()
                if tables:
                    # Use first table for now (could make this configurable)
                    table_name = tables[0]
                    state.signup_data = db.query_signups(table_name, limit=1000)
        
        # Add message to conversation history
        state.conversation_history.append({
            "role": "user",
            "content": message.message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process the query
        response = await process_chat_query(
            query=message.message,
            enrichment_data=state.enrichment_data,
            signup_data=state.signup_data,
            llm_client=state.llm_client,
            conversation_history=state.conversation_history
        )
        
        # Add response to history
        state.conversation_history.append({
            "role": "assistant",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        })
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chat message: {str(e)}")


@app.post("/api/analyze")
async def run_icp_analysis():
    """
    Run full ICP analysis on loaded data.
    
    Returns:
        Analysis results
    """
    if state.enrichment_data is None:
        raise HTTPException(status_code=400, detail="No enrichment data loaded")
    
    if state.signup_data is None:
        raise HTTPException(status_code=400, detail="No signup data loaded")
    
    try:
        # Initialize analyzer
        if state.llm_client is None:
            state.llm_client = get_default_client()
        
        analyzer = ICPAnalyzer(llm_client=state.llm_client)
        
        # Run analysis
        result = analyzer.analyze(
            signup_data=state.signup_data,
            customer_data=state.enrichment_data,
            max_customers=50
        )
        
        # Store result
        state.analysis_result = result
        
        # Get statistics
        stats = analyzer.get_match_statistics(result)
        
        # Format response
        return {
            "status": "success",
            "summary": result.summary,
            "statistics": stats,
            "top_matches": [
                {
                    "company_name": m.company_name,
                    "score": m.score,
                    "confidence": m.confidence,
                    "matching_attributes": m.matching_attributes[:3],  # Top 3
                    "reasoning": m.reasoning
                }
                for m in result.matches[:10]
            ],
            "patterns": result.patterns,
            "recommendations": result.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.delete("/api/reset")
async def reset_state():
    """Reset all application state."""
    state.reset()
    return {"status": "success", "message": "State reset successfully"}


# Helper functions

async def process_chat_query(
    query: str,
    enrichment_data: pd.DataFrame,
    signup_data: Optional[pd.DataFrame],
    llm_client: LLMClient,
    conversation_history: List[Dict[str, str]]
) -> ChatResponse:
    """
    Process a user query and generate response.
    
    Args:
        query: User's question
        enrichment_data: Enrichment CSV data
        signup_data: Signup data from database
        llm_client: LLM client for analysis
        conversation_history: Previous conversation
        
    Returns:
        ChatResponse with analysis
    """
    # Build context for LLM
    context_parts = []
    
    # Add data summaries
    context_parts.append("## Available Data\n")
    context_parts.append(f"### Enrichment Data")
    context_parts.append(f"- Rows: {len(enrichment_data)}")
    context_parts.append(f"- Columns: {', '.join(enrichment_data.columns)}")
    context_parts.append(f"- Sample:\n```\n{enrichment_data.head(3).to_string()}\n```\n")
    
    if signup_data is not None:
        context_parts.append(f"### Signup Data")
        context_parts.append(f"- Rows: {len(signup_data)}")
        context_parts.append(f"- Columns: {', '.join(signup_data.columns)}")
        context_parts.append(f"- Sample:\n```\n{signup_data.head(3).to_string()}\n```\n")
    
    context = "\n".join(context_parts)
    
    # Build system prompt
    system_prompt = """You are a data analysis assistant specializing in ICP (Ideal Customer Profile) analysis.

Your job is to:
1. Answer questions about enrichment data and signup data
2. Analyze ICP fit based on the available data
3. Provide insights about customer segments, trends, and patterns
4. Generate simple statistics and summaries
5. Use conversation history to understand context and answer follow-up questions

Guidelines:
- Be conversational and helpful
- Base answers on the actual data provided
- Use the conversation history to understand context - if the user asks a follow-up question, refer back to what was discussed previously
- When showing data, format it as tables with title, columns, and rows
- Keep responses concise but informative
- If you need to show charts, specify the data in a structured format
- Be honest about data limitations
- If the user refers to something mentioned earlier (like "those customers" or "the top 5"), use the conversation history to understand what they're referring to

Formatting:
- Use markdown formatting to make your responses more readable
- Use **bold** for emphasis on key findings or numbers
- Use bullet points (-) or numbered lists (1.) to break up information
- Use headings (##) to organize different sections when appropriate
- Break up long paragraphs into shorter, digestible chunks
- Use line breaks between paragraphs for better readability

Response Format:
Return a JSON object with this structure:
{
  "content": "Your conversational response text",
  "table": {
    "title": "Table title",
    "columns": ["Col1", "Col2"],
    "rows": [{"Col1": "val1", "Col2": "val2"}]
  },
  "charts": [
    {
      "id": "chart-id",
      "title": "Chart title",
      "data": [{"x": "value", "y": 10}],
      "xKey": "x",
      "yKey": "y",
      "meta": "Optional description"
    }
  ],
  "sql": "Optional SQL query (if relevant)"
}

Note: table, charts, and sql are optional. Only include them when relevant."""

    # Build user prompt with data context
    user_prompt = f"""# User Question
{query}

# Available Data Context
{context}

Please analyze the data and answer the user's question. If this is a follow-up question, use the conversation history to understand the context. Provide insights, tables, or charts as appropriate."""

    # Prepare conversation history for LLM (exclude the current message which is already in the prompt)
    # Include last 10 messages (5 exchanges) for context, but exclude the current query
    llm_conversation_history = []
    if len(conversation_history) > 1:
        # Get last messages before the current one (which was just added)
        for msg in conversation_history[:-1]:  # Exclude the last message (current query)
            llm_conversation_history.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        # Limit to last 10 messages to avoid token limits
        llm_conversation_history = llm_conversation_history[-10:]

    # Get LLM response with conversation history
    try:
        response_json = llm_client.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            conversation_history=llm_conversation_history if llm_conversation_history else None
        )
        
        # Parse and return
        return ChatResponse(
            content=response_json.get("content", "I couldn't generate a response. Please try rephrasing your question."),
            table=response_json.get("table"),
            charts=response_json.get("charts"),
            sql=response_json.get("sql")
        )
        
    except Exception as e:
        # Fallback to simple response
        return ChatResponse(
            content=f"I encountered an error analyzing your question: {str(e)}. Please try rephrasing or asking something else."
        )


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

