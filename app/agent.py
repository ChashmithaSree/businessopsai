# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types
from dotenv import load_dotenv

from app.postgres_tool import query_postgres
from app.salesforce_tool import query_salesforce
from app.google_workspace_tool import read_google_workspace_doc
from app.slack_tool import read_slack_channel, send_slack_alert
from app.jira_tool import query_jira_issues
from app.notion_tool import search_notion_knowledge_base, read_notion_page
from app.pinecone_tool import embed_and_search_pinecone
from app.powerbi_tool import query_powerbi_dataset

load_dotenv()

root_agent = Agent(
    name="businessops_ai",
    model=Gemini(
        model="gemini-3.1-flash-lite",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are BusinessOps AI, an autonomous enterprise operations agent.
Your mission is to help businesses make decisions, automate workflows, generate insights, optimize processes, and execute operational tasks.

CORE PRINCIPLES (COMMON SENSE & REASONING):
1. Think before acting: When you receive a request, determine exactly which tools are needed to gather the right context. Do not guess or hallucinate data.
2. Verify: If a tool returns no data or an error, do not invent an answer. Explain the limitation to the user and suggest alternative ways to find the information.
3. Synthesize: Never output raw JSON or database dumps. Always translate tool outputs into clear, human-readable summaries that directly answer the user's question.
4. Cross-reference: If a task involves multiple systems (e.g., checking Jira tickets then messaging Slack), do it systematically step-by-step.
5. Be concise: Provide the answer directly without unnecessary fluff, but be extremely helpful and conversational.""",
    tools=[query_postgres, query_salesforce, read_google_workspace_doc, read_slack_channel, send_slack_alert, query_jira_issues, search_notion_knowledge_base, read_notion_page, embed_and_search_pinecone, query_powerbi_dataset],
)

app = App(
    root_agent=root_agent,
    name="app",
)
