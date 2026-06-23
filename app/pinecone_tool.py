import os
import json
from pinecone import Pinecone

def embed_and_search_pinecone(query_text: str, top_k: int = 5) -> str:
    """Performs a semantic similarity search against the Pinecone vector database using raw text.
    
    Args:
        query_text: The plain text to search for (e.g., "What is the Q3 revenue goal?").
        top_k: The number of closest matching documents to return. Default is 5.
        
    Returns:
        A JSON string containing the matched documents/metadata, or an error.
    """
    api_key = os.environ.get("PINECONE_API_KEY")
    index_name = os.environ.get("PINECONE_INDEX_NAME")
    # Defaulting to a common Pinecone inference model; configurable via .env
    model_name = os.environ.get("PINECONE_EMBEDDING_MODEL", "multilingual-e5-large")
    
    # Safety Check: Ensure credentials exist
    if not api_key or not index_name:
        return json.dumps({"error": "Missing Pinecone configuration in environment variables (PINECONE_API_KEY, PINECONE_INDEX_NAME)."})
        
    try:
        # Initialize connection
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        
        # Generate vector embedding for the text using Pinecone's Inference API
        # This prevents the agent from needing to generate vectors itself
        embeddings = pc.inference.embed(
            model=model_name,
            inputs=[query_text],
            parameters={"input_type": "query"}
        )
        vector = embeddings[0].values
        
        # Perform read-only vector search
        response = index.query(
            vector=vector,
            top_k=min(top_k, 20),
            include_metadata=True
        )
        
        # Extract matching documents from metadata
        matches = []
        for match in response.get("matches", []):
            matches.append({
                "id": match.get("id"),
                "similarity_score": round(match.get("score", 0), 4),
                # Fallback if 'text' key is not present in metadata payload
                "content": match.get("metadata", {}).get("text", str(match.get("metadata", {})))
            })
            
        return json.dumps({"status": "success", "total_matches": len(matches), "matches": matches}, default=str)
        
    except Exception as e:
        return json.dumps({"error": f"Pinecone API Error: {str(e)}"})
