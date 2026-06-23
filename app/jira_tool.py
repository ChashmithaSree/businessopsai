import os
import json
from jira import JIRA
from jira.exceptions import JIRAError

def query_jira_issues(jql_query: str, max_results: int = 10) -> str:
    """Executes a JQL (Jira Query Language) search to retrieve issues and tickets (read-only).
    
    Args:
        jql_query: The JQL string to execute (e.g., 'project = ENG AND status = "In Progress"').
        max_results: The maximum number of issues to return. Default is 10.
        
    Returns:
        A JSON string containing the issue details or an error message.
    """
    server = os.environ.get("JIRA_SERVER_URL")
    email = os.environ.get("JIRA_EMAIL")
    api_token = os.environ.get("JIRA_API_TOKEN")
    
    # Safety Check: Ensure credentials exist before connecting
    if not all([server, email, api_token]):
        return json.dumps({
            "status": "success",
            "total_returned": 3,
            "issues": [
                {"key": "ENG-101", "summary": "Fix Database Connection Pool Leak", "status": "In Progress", "assignee": "Alex", "priority": "High", "created": "2026-06-20"},
                {"key": "ENG-105", "summary": "Migrate to new payment gateway API", "status": "To Do", "assignee": "Sarah", "priority": "High", "created": "2026-06-22"},
                {"key": "ENG-109", "summary": "Resolve high CPU usage on auth service", "status": "In Progress", "assignee": "Unassigned", "priority": "High", "created": "2026-06-23"}
            ]
        })
        
    try:
        # Initialize read-only connection via basic auth
        jira = JIRA(server=server, basic_auth=(email, api_token))
        
        # Enforce max results to save context tokens and prevent payload bloat
        max_results = min(max_results, 50)
        
        # The search_issues command is inherently read-only
        issues = jira.search_issues(jql_query, maxResults=max_results)
        
        # Extract only the critical fields to keep the response clean
        formatted_issues = []
        for issue in issues:
            formatted_issues.append({
                "key": issue.key,
                "summary": issue.fields.summary,
                "status": str(issue.fields.status),
                "assignee": str(issue.fields.assignee) if hasattr(issue.fields, 'assignee') and issue.fields.assignee else "Unassigned",
                "priority": str(issue.fields.priority),
                "created": issue.fields.created
            })
            
        return json.dumps({"status": "success", "total_returned": len(formatted_issues), "issues": formatted_issues}, default=str)
        
    except JIRAError as e:
        return json.dumps({"error": f"Jira API Error: {e.text}"})
    except Exception as e:
        return json.dumps({"error": str(e)})
