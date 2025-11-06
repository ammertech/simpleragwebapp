import os
import json
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Azure RAG Chat App")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Environment variables for Azure services
# In production, use Azure Key Vault or similar for secure storage
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, description="Number of search results to retrieve")
    filter: Optional[str] = Field(default=None, description="Optional filter for the search")

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query", response_model=ChatResponse)
async def query_documents(request: QueryRequest):
    try:
        # Step 1: Search for relevant documents in Azure AI Search
        search_results = await search_documents(request.query, request.top_k, request.filter)
        
        # Step 2: Generate answer with Azure OpenAI
        answer, sources = await generate_answer(request.query, search_results)
        
        return ChatResponse(answer=answer, sources=sources)
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

async def search_documents(query: str, top_k: int, filter_param: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for documents in Azure AI Search using both vector and semantic search
    """
    try:
        # Create search request body
        search_body = {
            "search": query,
            "queryType": "semantic",
            "vectorQueries": [
                {
                    "kind": "text",
                    "text": query,
                    "fields": "text_vector",
                    "k": top_k
                }
            ],
            "top": top_k
        }
        
        # Add filter if provided
        if filter_param:
            search_body["filter"] = filter_param
        
        # Set up search headers
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_SEARCH_KEY
        }
        
        # Make request to Azure AI Search
        async with httpx.AsyncClient() as client:
            search_url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}/docs/search?api-version=2023-10-01-preview"
            response = await client.post(
                search_url,
                headers=headers,
                json=search_body,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"Search API error: {response.status_code} {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            results = response.json()
            return results.get("value", [])
    
    except Exception as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise

async def generate_answer(query: str, search_results: List[Dict[str, Any]]) -> tuple[str, List[Dict[str, Any]]]:
    """
    Generate an answer using Azure OpenAI based on the query and search results
    """
    try:
        # Extract context from search results
        context_chunks = []
        sources = []
        
        for result in search_results:
            if "chunk" in result:
                context_chunks.append(result["chunk"])
            
            # Extract source information
            source = {
                "title": result.get("title", "Unknown Document"),
                "url": result.get("url", ""),
                "chunk_id": result.get("id", ""),
                "score": result.get("@search.score", 0)
            }
            sources.append(source)
        
        # Combine context chunks
        context = "\n\n".join(context_chunks)
        
        # Prepare the prompt for OpenAI
        messages = [
            {
                "role": "system", 
                "content": """You are a helpful assistant that provides information based on the context provided. 
                Follow these guidelines:
                1. Answer ONLY based on provided context
                2. If unsure, say "I don't have that information"
                3. Cite the source document name when possible
                4. Be concise but complete
                5. Use bullet points for lists
                6. Do not hallucinate or make up information
                """
            },
            {
                "role": "user", 
                "content": f"""Context:
                {context}
                
                Question: {query}
                
                Instructions:
                - Provide a direct answer
                - Cite the relevant document when possible
                - If multiple documents apply, summarize each
                """
            }
        ]
        
        # Create OpenAI request
        openai_body = {
            "messages": messages,
            "model": AZURE_OPENAI_DEPLOYMENT,
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        # Set up OpenAI headers
        headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_KEY
        }
        
        # Make request to Azure OpenAI
        async with httpx.AsyncClient() as client:
            openai_url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2023-05-15"
            response = await client.post(
                openai_url,
                headers=headers,
                json=openai_body,
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)
            
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            return answer, sources
    
    except Exception as e:
        logger.error(f"Error generating answer: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
