import json
from typing import TypedDict, Annotated, Literal, List, Dict, Optional
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import config


class AgentState(TypedDict):
    """
    This state tracks the entire research process from initial 
    query through research, analysis, and report generation.
    """
    # Core conversation messages
    messages: Annotated[List[BaseMessage], "Chat messages between user and agent"]
    
    # Research query and context
    research_query: str  # Original research question/topic
    research_scope: Optional[str]  # Refined or expanded scope
    
    # Research organization
    sections: Annotated[List[str], "List of research sections/topics to cover"]
    current_section: Optional[str]  # Currently being researched
    
    # Research data
    research_results: Annotated[
        Dict[str, List[Dict]], 
        "Research results organized by section/topic"
    ]
    search_queries: Annotated[List[str], "List of search queries executed"]
    
    # Report generation
    report_draft: str  # Accumulated report content
    report_sections: Annotated[Dict[str, str], "Report sections by topic"]
    
    # Reflection and quality control
    reflection_feedback: Optional[str]  # Self-reflection on research quality
    iteration_count: int  # Number of research iterations
    research_complete: bool  # Flag indicating if research is done
    
    # Metadata
    sources: Annotated[List[Dict], "List of sources with URLs and metadata"]
    confidence_score: Optional[float]  # Confidence in research completeness


def initialize_deepseek_llm():
    """Initialize DeepSeek LLM using LangChain. 
    DeepSeek API is OpenAI-compatible, so we use 
    ChatOpenAI with DeepSeek's base URL and API key.
    """
    llm = ChatOpenAI(
        model=config.DEEPSEEK_MODEL,
        base_url=config.DEEPSEEK_BASE_URL,
        api_key=config.DEEPSEEK_API_KEY,
        temperature=config.DEEPSEEK_TEMPERATURE,
        max_tokens=config.DEEPSEEK_MAX_TOKENS,
    )
    return llm

# ===== NODE 1 : Create Research Agent Graph =====
def create_research_agent():
    """Create and configure the deep research agent graph."""
    llm = initialize_deepseek_llm()
    
    search_tool = TavilySearchResults(
        max_results=config.TAVILY_MAX_RESULTS,
        search_depth=config.TAVILY_SEARCH_DEPTH,
        tavily_api_key=config.TAVILY_API_KEY,
    )
    
    def generate_queries(state: AgentState) -> AgentState:
        """LLM generates sub-queries based on research topic.
        Breaks down the main research query into specific search queries
        and identifies sections to research.
        """
        query = state["research_query"]
        sections = state.get("sections", [])
        
        if sections:
            return state
        
        prompt = f"""You are a research assistant. Break down the following research query into 3-5 specific search queries and identify key sections to research.

Research Query: {query}

Generate:
1. A list of 3-5 specific search queries (each should be focused and searchable)
2. A list of 3-5 research sections/topics to cover

Respond in JSON format:
{{
    "queries": ["query1", "query2", ...],
    "sections": ["section1", "section2", ...]
}}"""

        messages = [
            SystemMessage(content="You are a research assistant that breaks down complex topics into searchable queries."),
            HumanMessage(content=prompt)
        ]
        
        response = llm.invoke(messages)
        content = response.content
        
        # Parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(content)
            queries = parsed.get("queries", [])
            sections = parsed.get("sections", [])
        except (json.JSONDecodeError, KeyError):
            # Fallback: try to extract queries from text
            queries = [query]  # Use original query as fallback
            sections = ["Overview", "Details", "Conclusion"]
        
        current_messages = state.get("messages", [])
        return {
            "search_queries": queries,
            "sections": sections,
            "messages": current_messages + [response],
        }
    
    # ===== NODE 2: Search Sections =====
    def search_sections(state: AgentState) -> AgentState:
        """Parallel map over sub-queries → call search tool → summarize results.
        For each search query, performs a search and summarizes the results.
        """
        queries = state.get("search_queries", [])
        sections = state.get("sections", [])
        research_results = state.get("research_results", {})
        sources = state.get("sources", [])
        
        if not queries:
            return state
        
        # Process each query
        for i, query in enumerate(queries):
            section = sections[i] if i < len(sections) else f"Section {i+1}"
            
            # Perform search
            search_results = search_tool.invoke({"query": query})
            
            # Extract sources
            for result in search_results:
                if isinstance(result, dict):
                    sources.append({
                        "url": result.get("url", ""),
                        "title": result.get("title", ""),
                        "content": result.get("content", "")[:500],  # Truncate
                    })
            
            # Summarize results using LLM
            results_text = "\n\n".join([
                f"Title: {r.get('title', 'N/A')}\nContent: {r.get('content', 'N/A')[:300]}"
                for r in search_results[:3]  # Top 3 results
            ])
            
            summary_prompt = f"""Summarize the following search results for the query: "{query}"

Search Results:
{results_text}

Provide a concise summary (2-3 sentences) of the key findings."""

            summary_messages = [
                SystemMessage(content="You are a research assistant that summarizes search results."),
                HumanMessage(content=summary_prompt)
            ]
            
            summary_response = llm.invoke(summary_messages)
            summary = summary_response.content
            
            # Store results by section
            if section not in research_results:
                research_results[section] = []
            
            research_results[section].append({
                "query": query,
                "summary": summary,
                "raw_results": search_results[:3],  # Store top 3
            })
        
        return {
            "research_results": research_results,
            "sources": sources,
            "iteration_count": state.get("iteration_count", 0) + 1,
        }
    
    # ===== NODE 3: Reflect =====
    def reflect(state: AgentState) -> AgentState:
        """LLM scores completeness (0-10) and suggests next actions.
        
        Evaluates the current research state and provides feedback.
        """
        query = state["research_query"]
        sections = state.get("sections", [])
        research_results = state.get("research_results", {})
        iteration = state.get("iteration_count", 0)
        
        # Build research status
        status = f"Research Query: {query}\n\n"
        status += f"Sections to cover: {', '.join(sections)}\n\n"
        status += "Current Research Status:\n"
        
        for section in sections:
            if section in research_results:
                summaries = [r.get("summary", "") for r in research_results[section]]
                status += f"- {section}: {len(summaries)} summaries collected\n"
            else:
                status += f"- {section}: Not yet researched\n"
        
        reflection_prompt = f"""Evaluate the completeness of this research:

{status}

Rate the research completeness on a scale of 0-10 and provide:
1. Completeness score (0-10)
2. What's missing or needs improvement
3. Suggested next actions (if score < 8)

Respond in JSON format:
{{
    "score": 7,
    "feedback": "What's missing...",
    "next_actions": ["action1", "action2"],
    "is_complete": false
}}"""

        reflection_messages = [
            SystemMessage(content="You are a research quality evaluator."),
            HumanMessage(content=reflection_prompt)
        ]
        
        reflection_response = llm.invoke(reflection_messages)
        content = reflection_response.content
        
        # Parse reflection
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            parsed = json.loads(content)
            score = parsed.get("score", 5)
            feedback = parsed.get("feedback", "No feedback provided")
            next_actions = parsed.get("next_actions", [])
            is_complete = parsed.get("is_complete", score >= 8)
        except (json.JSONDecodeError, KeyError):
            # Fallback
            score = 5
            feedback = "Unable to parse reflection"
            next_actions = []
            is_complete = iteration >= config.MAX_ITERATIONS
        
        current_messages = state.get("messages", [])
        return {
            "reflection_feedback": feedback,
            "confidence_score": score / 10.0,  # Normalize to 0-1
            "research_complete": is_complete or iteration >= config.MAX_ITERATIONS,
            "messages": current_messages + [reflection_response],
        }
    
    # ===== NODE 4: Write Report =====
    def write_report(state: AgentState) -> AgentState:
        """Final synthesis: compile all research into a comprehensive report."""
        query = state["research_query"]
        sections = state.get("sections", [])
        research_results = state.get("research_results", {})
        sources = state.get("sources", [])
        
        # Build research content for report
        research_content = f"# Research Report: {query}\n\n"
        
        for section in sections:
            research_content += f"## {section}\n\n"
            
            if section in research_results:
                for result in research_results[section]:
                    research_content += f"{result.get('summary', 'No summary')}\n\n"
            else:
                research_content += "No research data available for this section.\n\n"
        
        # Generate final report using LLM
        report_prompt = f"""Based on the following research findings, write a comprehensive, well-structured research report.

Research Query: {query}

Research Findings:
{research_content}

Write a professional research report with:
1. Executive Summary
2. Detailed findings for each section
3. Key insights and conclusions
4. References to sources

Format the report in markdown."""

        report_messages = [
            SystemMessage(content="You are a professional research report writer."),
            HumanMessage(content=report_prompt)
        ]
        
        report_response = llm.invoke(report_messages)
        report_draft = report_response.content
        
        # Add sources section
        if sources:
            report_draft += "\n\n## Sources\n\n"
            for i, source in enumerate(sources[:10], 1):  # Top 10 sources
                report_draft += f"{i}. [{source.get('title', 'Untitled')}]({source.get('url', '#')})\n"
        
        current_messages = state.get("messages", [])
        return {
            "report_draft": report_draft,
            "research_complete": True,
            "messages": current_messages + [report_response],
        }
    
    # ===== ROUTING FUNCTIONS =====
    def should_continue_research(state: AgentState) -> Literal["reflect", "write_report"]:
        """Route based on research completeness."""
        if state.get("research_complete", False):
            return "write_report"
        return "reflect"
    
    def should_continue_after_reflection(state: AgentState) -> Literal["search_sections", "write_report"]:
        """Route based on reflection feedback."""
        if state.get("research_complete", False):
            return "write_report"
        # Could add more search queries if needed
        return "write_report"  # For now, go to report after reflection
    
    # ===== BUILD GRAPH =====
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("generate_queries", generate_queries)
    workflow.add_node("search_sections", search_sections)
    workflow.add_node("reflect", reflect)
    workflow.add_node("write_report", write_report)
    
    # Set entry point
    workflow.set_entry_point("generate_queries")
    
    # Add edges
    workflow.add_edge("generate_queries", "search_sections")
    workflow.add_edge("search_sections", "reflect")
    workflow.add_conditional_edges(
        "reflect",
        should_continue_after_reflection,
        {
            "search_sections": "search_sections",  # Could loop back for more research
            "write_report": "write_report",
        },
    )
    workflow.add_edge("write_report", END)
    
    # Add memory if enabled
    memory = None
    if config.ENABLE_MEMORY:
        memory = MemorySaver()
    
    # Compile the graph
    app = workflow.compile(checkpointer=memory)
    
    return app


def run_research(query: str, agent=None):
    """Run a research query through the agent."""
    if agent is None:
        agent = create_research_agent()
    
    # Initialize comprehensive state
    initial_state: AgentState = {
        "messages": [HumanMessage(content=query)],
        "research_query": query,
        "research_scope": None,
        "sections": [],
        "current_section": None,
        "research_results": {},
        "search_queries": [],
        "report_draft": "",
        "report_sections": {},
        "reflection_feedback": None,
        "iteration_count": 0,
        "research_complete": False,
        "sources": [],
        "confidence_score": None,
    }
    
    config_dict = {"configurable": {"thread_id": "1"}}
    result = agent.invoke(initial_state, config_dict)
    
    return result

