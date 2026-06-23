import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly', 
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

def read_google_workspace_doc(document_id: str, doc_type: str = "document") -> str:
    """Reads the content of a Google Document or Spreadsheet securely (read-only).
    
    Args:
        document_id: The ID of the Google Doc or Sheet (found in the URL).
        doc_type: Either 'document' or 'spreadsheet'. Default is 'document'.
        
    Returns:
        A JSON string containing the document content or an error message.
    """
    credentials_json = os.environ.get("GOOGLE_WORKSPACE_CREDENTIALS_JSON")
    if not credentials_json:
        return json.dumps({"error": "Missing GOOGLE_WORKSPACE_CREDENTIALS_JSON environment variable. Please provide a valid Service Account JSON string."})
        
    try:
        # Safely load the service account credentials
        creds_dict = json.loads(credentials_json)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        
        if doc_type.lower() == "spreadsheet":
            service = build('sheets', 'v4', credentials=creds)
            
            # Retrieve sheet metadata to find the first sheet name
            sheet_metadata = service.spreadsheets().get(spreadsheetId=document_id).execute()
            sheets = sheet_metadata.get('sheets', '')
            if not sheets:
                return json.dumps({"error": "No sheets found in spreadsheet."})
            
            title = sheets[0].get("properties", {}).get("title", "Sheet1")
            
            # Fetch all values from the first sheet
            result = service.spreadsheets().values().get(spreadsheetId=document_id, range=title).execute()
            values = result.get('values', [])
            return json.dumps({"status": "success", "type": "spreadsheet", "data": values}, default=str)
            
        else: 
            # Default to Document processing
            service = build('docs', 'v1', credentials=creds)
            document = service.documents().get(documentId=document_id).execute()
            
            # Extract plain text from Google Docs complex element structure
            content = ""
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for p_element in element.get('paragraph').get('elements', []):
                        if 'textRun' in p_element:
                            content += p_element.get('textRun').get('content')
                            
            return json.dumps({"status": "success", "type": "document", "content": content}, default=str)
            
    except Exception as e:
        return json.dumps({"error": str(e)})
