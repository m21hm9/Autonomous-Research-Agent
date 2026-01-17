import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the project root
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Model Configuration
DEEPSEEK_MODEL = "deepseek-chat"  # or "deepseek-reasoner" for reasoning
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_TEMPERATURE = 0.7
DEEPSEEK_MAX_TOKENS = 4096

# Search Configuration
TAVILY_MAX_RESULTS = 5
TAVILY_SEARCH_DEPTH = "advanced"  # "basic" or "advanced"

# Agent Configuration
MAX_ITERATIONS = 10
ENABLE_MEMORY = True

# Validate required keys
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not found in environment variables")

