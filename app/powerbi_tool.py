import os
import json
import requests
import msal

def query_powerbi_dataset(dataset_id: str, dax_query: str) -> str:
    """Executes a read-only DAX query against a Power BI dataset to retrieve aggregated analytics.
    
    Args:
        dataset_id: The ID of the Power BI dataset.
        dax_query: The DAX (Data Analysis Expressions) query string. Must be an EVALUATE statement.
        
    Returns:
        A JSON string containing the query results or an error.
    """
    # Safety constraint: Read-only access
    if not dax_query.strip().upper().startswith("EVALUATE"):
        return json.dumps({"error": "Safety Constraint Violation: Only EVALUATE DAX queries are permitted to ensure read-only analytics access."})

    client_id = os.environ.get("PBI_CLIENT_ID")
    client_secret = os.environ.get("PBI_CLIENT_SECRET")
    tenant_id = os.environ.get("PBI_TENANT_ID")
    
    # Safety Check: Ensure Azure AD credentials exist
    if not all([client_id, client_secret, tenant_id]):
        return json.dumps({"error": "Missing Power BI configuration in environment variables (PBI_CLIENT_ID, PBI_CLIENT_SECRET, PBI_TENANT_ID)."})

    authority = f"https://login.microsoftonline.com/{tenant_id}"
    scope = ["https://analysis.windows.net/powerbi/api/.default"]
    
    try:
        # Authenticate securely via Azure AD (Microsoft Entra ID) using a Service Principal
        app = msal.ConfidentialClientApplication(
            client_id, authority=authority, client_credential=client_secret
        )
        
        result = app.acquire_token_silent(scope, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=scope)
            
        if "access_token" not in result:
            return json.dumps({"error": "Failed to acquire Azure AD token.", "details": result.get("error_description")})
            
        access_token = result["access_token"]
        
        # Execute the DAX query against the Power BI REST API
        endpoint = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/executeQueries"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "queries": [{"query": dax_query}],
            "serializerSettings": {"includeNulls": True}
        }
        
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        # Parse the deeply nested response to return a clean JSON array
        data = response.json()
        results = data.get("results", [])
        if results and len(results) > 0:
            tables = results[0].get("tables", [])
            if tables and len(tables) > 0:
                rows = tables[0].get("rows", [])
                return json.dumps({"status": "success", "total_rows": len(rows), "data": rows}, default=str)
            
        return json.dumps({"status": "success", "data": []})
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_msg = e.response.json()
            except ValueError:
                error_msg = e.response.text
        return json.dumps({"error": f"Power BI API Error: {error_msg}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
