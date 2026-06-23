import os
import json
from simple_salesforce import Salesforce

def query_salesforce(soql_query: str) -> str:
    """Executes a read-only SOQL query against Salesforce to retrieve CRM data (leads, opportunities, etc).
    
    Args:
        soql_query: The SOQL query string to execute. Must be a SELECT statement.
        
    Returns:
        A JSON string containing the query results or an error message.
    """
    # Safety constraint: Read-only access
    if not soql_query.strip().upper().startswith("SELECT"):
        return json.dumps({"error": "Safety Constraint Violation: Only SELECT SOQL queries are permitted."})

    # Validate credentials exist
    if not os.environ.get("SF_USERNAME") or not os.environ.get("SF_PASSWORD"):
        return json.dumps({"error": "Missing Salesforce credentials in environment variables (SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN)."})

    try:
        # Connect using environment variables
        sf = Salesforce(
            username=os.environ.get("SF_USERNAME"),
            password=os.environ.get("SF_PASSWORD"),
            security_token=os.environ.get("SF_SECURITY_TOKEN", ""),
            domain=os.environ.get("SF_DOMAIN", "login") # 'login' for production, 'test' for sandbox
        )
        
        # Execute query
        results = sf.query_all(soql_query)
        records = results.get("records", [])
        
        # Clean up internal Salesforce metadata from records to save context tokens
        for record in records:
            if "attributes" in record:
                del record["attributes"]
                
        return json.dumps({
            "status": "success", 
            "total_size": results.get("totalSize", len(records)), 
            "data": records
        }, default=str)
        
    except Exception as e:
        return json.dumps({"error": str(e)})
