# 🔍 DeepSeek Research Agent

An autonomous research agent powered by DeepSeek LLM and Tavily search, built with LangGraph.

## Features

- **Intelligent Query Generation**: Breaks down research topics into focused search queries
- **Parallel Search**: Uses Tavily to search multiple queries simultaneously
- **Smart Summarization**: LLM-powered summarization of search results
- **Self-Reflection**: Evaluates research completeness (0-10 score)
- **Report Generation**: Creates comprehensive markdown reports with sources

## Setup

### 1. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit `.env` file and add your API keys:

```env
DEEPSEEK_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

- **DeepSeek**: Get your key from https://platform.deepseek.com/api_keys
- **Tavily**: Get your key from https://app.tavily.com

## Running the Agent

### Option 1: Streamlit UI (Recommended)

Launch the interactive web interface:

```bash
streamlit run app.py
```

Then:
1. Open your browser to the URL shown (usually `http://localhost:8501`)
2. Click "Initialize Agent" in the sidebar
3. Enter your research query
4. Click "🔍 Research"
5. View the generated report and results

### Option 2: Command Line Test Script

Run a quick test:

```bash
python test_agent.py
```

This will:
- Check your API keys
- Run a test query
- Display results in the terminal

### Option 3: Python Script

Use the agent programmatically:

```python
from agent import create_research_agent, run_research

# Create agent
agent = create_research_agent()

# Run research
result = run_research("What are the latest AI developments?")

# Access results
print(result["report_draft"])
print(result["confidence_score"])
print(result["sources"])
```

## Project Structure

```
my-deepseek-researcher/
├── agent.py          # Main LangGraph agent logic
├── app.py            # Streamlit UI
├── config.py         # Configuration and API keys
├── test_agent.py     # Test script
├── .env              # API keys (not committed)
└── README.md         # This file
```

## How It Works

The agent follows this workflow:

1. **Generate Queries** → Breaks down research topic into specific search queries
2. **Search Sections** → Performs parallel searches using Tavily
3. **Reflect** → Evaluates completeness and quality (0-10 score)
4. **Write Report** → Synthesizes findings into a comprehensive report

## Configuration

Edit `config.py` to customize:

- `DEEPSEEK_MODEL`: Model to use ("deepseek-chat" or "deepseek-reasoner")
- `TAVILY_MAX_RESULTS`: Number of search results per query (default: 5)
- `TAVILY_SEARCH_DEPTH`: "basic" or "advanced" (default: "advanced")
- `MAX_ITERATIONS`: Maximum research iterations (default: 10)

## Troubleshooting

### API Key Errors
- Make sure `.env` file exists and contains valid keys
- Keys should not have quotes around them
- Restart your terminal/IDE after adding keys

### Import Errors
- Make sure you're in the project directory
- Run `uv sync` or `pip install -r requirements.txt`
- Activate virtual environment if using one

### Search Errors
- Check your Tavily API key is valid
- Verify you have API credits/quota
- Check internet connection

## Example Queries

Try these research queries:

- "What are the latest developments in AI reasoning models?"
- "Compare different approaches to autonomous agents"
- "What is the current state of quantum computing?"
- "Recent breakthroughs in climate change solutions"

## License

MIT

