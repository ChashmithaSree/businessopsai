import os
import json
from notion_client import Client
from notion_client.errors import APIResponseError

def search_notion_knowledge_base(query: str, limit: int = 5) -> str:
    """Searches the Notion workspace for pages matching the query string.
    
    Args:
        query: The search term to look for in page titles.
        limit: Maximum number of pages to return. Default is 5.
        
    Returns:
        A JSON string containing the page IDs and titles, or an error.
    """
    token = os.environ.get("NOTION_API_KEY")
    if not token:
        if "Database" in query or "ENG-101" in query or "Connection" in query:
            return json.dumps({"status": "success", "results": [{"id": "page_db_123", "title": "Database Architecture & Connection Pools", "url": "notion.so/db-arch"}]})
        elif "Q3" in query or "roadmap" in query.lower():
            return json.dumps({"status": "success", "results": [{"id": "page_q3_789", "title": "Q3 Engineering Roadmap", "url": "notion.so/q3-roadmap"}]})
        return json.dumps({"status": "success", "results": [{"id": "page_gen_456", "title": "General Engineering Guidelines", "url": "notion.so/gen-eng"}]})
        
    try:
        notion = Client(auth=token)
        response = notion.search(query=query, page_size=min(limit, 20))
        
        results = []
        for r in response.get("results", []):
            if r.get("object") == "page":
                # Handle Notion's deeply nested property structure safely
                title = "Untitled"
                props = r.get("properties", {})
                
                # Pages in databases have arbitrary title column names, standard pages use "title"
                for key, val in props.items():
                    if val.get("type") == "title":
                        title_arr = val.get("title", [])
                        if title_arr:
                            title = title_arr[0].get("plain_text", "Untitled")
                        break
                
                results.append({
                    "id": r["id"],
                    "title": title,
                    "url": r.get("url")
                })
                
        return json.dumps({"status": "success", "results": results}, default=str)
        
    except APIResponseError as e:
        return json.dumps({"error": f"Notion API Error: {str(e)}"})

def read_notion_page(page_id: str) -> str:
    """Reads the text content of a specific Notion page. Use search_notion_knowledge_base to find the page_id.
    
    Args:
        page_id: The ID of the Notion page to read.
        
    Returns:
        A JSON string containing the plain text of the page.
    """
    token = os.environ.get("NOTION_API_KEY")
    if not token:
        if page_id == "page_db_123":
            return json.dumps({"status": "success", "content": "Database Connection Pools:\nOur primary PostgreSQL DB is hosted on AWS. If connections leak, usually it's caused by the auth microservice failing to close connections during timeout. To fix, reboot the auth pod and update the timeout config in secrets."})
        elif page_id == "page_q3_789":
            return json.dumps({"status": "success", "content": "Q3 Engineering Roadmap:\n1. Launch new payment gateway API.\n2. Scale auth service CPU limits to handle 2x traffic.\n3. Implement proper database connection pooling."})
        return json.dumps({"status": "success", "content": "Welcome to Engineering Notion. Ensure all PRs are reviewed by 2 people before merging."})
        
    try:
        notion = Client(auth=token)
        # Fetch the top-level blocks of the page
        blocks = notion.blocks.children.list(block_id=page_id).get("results", [])
        
        content = ""
        for block in blocks:
            block_type = block.get("type")
            if block_type and block_type in block:
                # Extract text from supported block types (paragraphs, headings, lists)
                rich_text = block[block_type].get("rich_text", [])
                for t in rich_text:
                    content += t.get("plain_text", "")
                content += "\n"
                
        return json.dumps({"status": "success", "content": content.strip()})
        
    except APIResponseError as e:
        return json.dumps({"error": f"Notion API Error: {str(e)}"})
