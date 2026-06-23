import os
import psycopg2
import json

def query_postgres(query: str) -> str:
    """Executes a read-only SELECT query against the PostgreSQL database.
    
    Args:
        query: The SQL query string to execute. Must be a SELECT statement.
        
    Returns:
        A JSON string containing the query results or an error message.
    """
    # Safety constraint: Read-only access
    if not query.strip().upper().startswith("SELECT"):
        return json.dumps({"error": "Safety Constraint Violation: Only SELECT queries are permitted."})

    try:
        # Connect using environment variables
        conn = psycopg2.connect(
            host=os.environ.get("PG_HOST", "localhost"),
            port=os.environ.get("PG_PORT", "5432"),
            dbname=os.environ.get("PG_DATABASE", "business_db"),
            user=os.environ.get("PG_USER", "postgres"),
            password=os.environ.get("PG_PASSWORD", "postgres")
        )
        
        # Defense in depth: Force session to read-only
        conn.set_session(readonly=True, autocommit=True)
        
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Retrieve column headers
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch rows and map to dictionary
        results = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in results]
        
        cursor.close()
        conn.close()
        
        return json.dumps({"status": "success", "rows_returned": len(data), "data": data}, default=str)
        
    except Exception as e:
        return json.dumps({"error": str(e)})
