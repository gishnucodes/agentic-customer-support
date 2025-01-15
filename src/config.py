import os
from datetime import datetime

# Environment configuration
class Config:
    GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
    DATABASE_PATH = '../data/mydatabase.db'
    LANGSMITH_TRACING = True
    LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY = "YOUR_LANGSMITH_API_KEY"
    LANGSMITH_PROJECT = "YOUR_PROJECT_NAME"
    POLICY_URL = "https://raw.githubusercontent.com/gishnucodes/agentic-customer-support/refs/heads/main/agent-policy.md"
    DB_PATH = os.path.join(os.path.dirname(__file__), '../data/mydatabase.db')