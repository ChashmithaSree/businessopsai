import asyncio
from app.agent import root_agent

async def main():
    print("Sending cross-functional query to BusinessOps AI...\n")
    query = "Analyze the open engineering tickets in Jira, check the Q3 roadmap in Notion, and draft a status update alert to the Slack engineering channel."
    print(f"Prompt: '{query}'\n")
    print("-" * 50)
    try:
        response = await root_agent.run(input=query)
        print("\nAgent Response:\n")
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
