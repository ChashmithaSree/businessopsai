import os
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def read_slack_channel(channel_id: str, limit: int = 10) -> str:
    """Reads recent messages from a specific Slack channel to gather context or monitor sentiment.
    
    Args:
        channel_id: The Slack channel ID (e.g., 'C1234567890').
        limit: Number of recent messages to retrieve (max 50). Default is 10.
        
    Returns:
        A JSON string containing the messages or an error.
    """
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        return json.dumps({"status": "success", "messages": [{"user": "U1234", "text": "Are we seeing elevated CPU on auth?", "timestamp": "1672531200.000100"}]})
        
    try:
        client = WebClient(token=token)
        limit = min(limit, 50) # Cap limit to prevent massive context window usage
        
        result = client.conversations_history(channel=channel_id, limit=limit)
        messages = result.get("messages", [])
        
        # Extract only relevant text to save tokens
        formatted_messages = []
        for msg in messages:
            if msg.get("type") == "message" and "text" in msg:
                formatted_messages.append({
                    "user": msg.get("user", "unknown"),
                    "text": msg.get("text"),
                    "timestamp": msg.get("ts")
                })
                
        return json.dumps({"status": "success", "messages": formatted_messages}, default=str)
        
    except SlackApiError as e:
        return json.dumps({"error": f"Slack API Error: {e.response['error']}"})

def send_slack_alert(channel_id: str, message: str) -> str:
    """Sends an internal alert or notification to a Slack channel.
    
    Args:
        channel_id: The Slack channel ID to send the message to.
        message: The text of the alert.
        
    Returns:
        A JSON string indicating success or failure.
    """
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        safe_message = f"[BusinessOps AI Automated Alert]\n{message}"
        print(f"MOCK SLACK SEND to {channel_id}: {safe_message}")
        return json.dumps({"status": "success", "message_ts": "1672531200.000200"})
        
    try:
        client = WebClient(token=token)
        
        # Safety constraint enforcement: Tag as automated agent to prevent impersonation
        safe_message = f"[BusinessOps AI Automated Alert]\n{message}"
        
        result = client.chat_postMessage(channel=channel_id, text=safe_message)
        return json.dumps({"status": "success", "message_ts": result.get("ts")})
        
    except SlackApiError as e:
        return json.dumps({"error": f"Slack API Error: {e.response['error']}"})
