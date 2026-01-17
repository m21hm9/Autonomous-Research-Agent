import streamlit as st
from agent import create_research_agent, run_research
import config

# Page configuration
st.set_page_config(
    page_title="DeepSeek Research Agent",
    page_icon="🔍",
    layout="wide",
)

# Initialize session state
if "agent" not in st.session_state:
    st.session_state.agent = None
if "research_history" not in st.session_state:
    st.session_state.research_history = []


def main():
    """Main Streamlit application."""
    st.title("🔍 DeepSeek Research Agent")
    st.markdown("An autonomous research agent powered by DeepSeek and Tavily search.")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        st.info(f"Model: {config.DEEPSEEK_MODEL}")
        st.info(f"Max Results: {config.TAVILY_MAX_RESULTS}")
        st.info(f"Search Depth: {config.TAVILY_SEARCH_DEPTH}")
        
        if st.button("Initialize Agent"):
            with st.spinner("Initializing agent..."):
                try:
                    st.session_state.agent = create_research_agent()
                    st.success("Agent initialized successfully!")
                except Exception as e:
                    st.error(f"Error initializing agent: {str(e)}")
    
    # Main content area
    st.header("Research Query")
    
    # Query input
    query = st.text_area(
        "Enter your research query:",
        height=100,
        placeholder="e.g., What are the latest developments in AI reasoning?",
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        research_button = st.button("🔍 Research", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("Clear History", use_container_width=True)
    
    if clear_button:
        st.session_state.research_history = []
        st.rerun()
    
    # Run research
    if research_button and query:
        if st.session_state.agent is None:
            st.warning("Please initialize the agent first from the sidebar.")
        else:
            with st.spinner("Researching..."):
                try:
                    result = run_research(query, st.session_state.agent)
                    
                    # Store in history
                    st.session_state.research_history.append({
                        "query": query,
                        "result": result,
                    })
                    
                    # Display results
                    st.success("Research completed!")
                    
                    # Show report draft (main output)
                    if result.get("report_draft"):
                        st.subheader("📄 Research Report")
                        st.markdown(result["report_draft"])
                    
                    # Show research progress
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Sections", len(result.get("sections", [])))
                    with col2:
                        st.metric("Search Queries", len(result.get("search_queries", [])))
                    with col3:
                        confidence = result.get("confidence_score", 0)
                        if confidence:
                            st.metric("Confidence", f"{confidence*100:.1f}%")
                    
                    # Show sections and research results
                    if result.get("sections"):
                        st.subheader("📚 Research Sections")
                        for section in result.get("sections", []):
                            with st.expander(f"Section: {section}"):
                                if section in result.get("research_results", {}):
                                    for res in result["research_results"][section]:
                                        st.markdown(f"**Query:** {res.get('query', 'N/A')}")
                                        st.markdown(f"**Summary:** {res.get('summary', 'N/A')}")
                                else:
                                    st.info("No research data for this section yet.")
                    
                    # Show reflection feedback
                    if result.get("reflection_feedback"):
                        st.subheader("🤔 Reflection & Quality Assessment")
                        st.info(result["reflection_feedback"])
                    
                    # Show sources
                    if result.get("sources"):
                        st.subheader("🔗 Sources")
                        for i, source in enumerate(result["sources"][:10], 1):
                            st.markdown(f"{i}. [{source.get('title', 'Untitled')}]({source.get('url', '#')})")
                    
                    # Show raw messages (for debugging)
                    with st.expander("🔍 Debug: Messages"):
                        for message in result.get("messages", []):
                            if hasattr(message, "content"):
                                st.markdown(f"**{message.__class__.__name__}:**")
                                st.text(message.content[:500])  # Truncate for display
                
                except Exception as e:
                    st.error(f"Error during research: {str(e)}")
                    st.exception(e)
    
    # Research history
    if st.session_state.research_history:
        st.header("Research History")
        for i, item in enumerate(reversed(st.session_state.research_history), 1):
            with st.expander(f"Query {i}: {item['query'][:50]}..."):
                st.markdown(f"**Query:** {item['query']}")
                st.json(item["result"])


if __name__ == "__main__":
    main()

