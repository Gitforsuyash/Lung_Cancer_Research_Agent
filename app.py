import streamlit as st
import json
from pathlib import Path
from rag_pipeline import RAGPipeline
from session_manager import SessionManager, check_and_setup
from config import *

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        padding: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        background: black;
    }
    .answer-box {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1E88E5;
        background: black;
    }
    .session-info {
        background-color: #fff3cd;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #f8d7da;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_pipeline' not in st.session_state:
    st.session_state.rag_pipeline = None
if 'session_manager' not in st.session_state:
    st.session_state.session_manager = SessionManager()
if 'setup_complete' not in st.session_state:
    st.session_state.setup_complete = False

# Header
st.markdown('<p class="main-header">🫁 Lung Cancer Research RAG Chatbot</p>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Session Info
with st.sidebar:
    st.header("📊 Session Information")
    
    session_info = st.session_state.session_manager.get_session_info()
    
    # Session counter
    if session_info['cleanup_needed']:
        st.markdown(f"""
        <div class="warning-box">
            <strong>⚠️ Cleanup Required!</strong><br>
            Maximum sessions reached. Data will be cleaned and re-downloaded.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="session-info">
            <strong>Session:</strong> {session_info['current_session']}/{session_info['max_sessions']}<br>
            <strong>Remaining:</strong> {session_info['remaining_sessions']} sessions
        </div>
        """, unsafe_allow_html=True)
    
    st.metric("Current Session", session_info['current_session'])
    st.metric("Sessions Remaining", session_info['remaining_sessions'])
    
    st.markdown("---")
    
    # Mode selection
    st.header("🎯 Mode")
    mode = st.radio(
        "Choose mode:",
        ["💬 Q&A Mode", "📄 Summarization Mode"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Admin controls
    with st.expander("⚙️ Admin Controls"):
        if st.button("🔄 Reset Session Counter"):
            st.session_state.session_manager.reset_counter()
            st.success("✅ Counter reset!")
            st.rerun()
        
        if st.button("🗑️ Force Cleanup Now"):
            with st.spinner("Cleaning up data..."):
                st.session_state.session_manager.force_cleanup()
                st.session_state.setup_complete = False
                st.session_state.rag_pipeline = None
            st.success("✅ Cleanup complete!")
            st.info("Please restart the app to re-download data.")
            st.stop()
    
    st.markdown("---")
    st.info("💡 **Note:** Data automatically cleans after 10 sessions.")

# Main content
def initialize_system():
    """Initialize or check system setup"""
    
    # Check if data exists
    data_exists, session_mgr = check_and_setup()
    
    if not data_exists:
        st.warning("⚠️ No data found. Please run setup first!")
        st.info("Run: `python setup_all.py` in your terminal")
        st.stop()
    
    # Increment session count
    with st.spinner("Loading RAG system..."):
        cleanup_triggered = session_mgr.increment_session()
        
        if cleanup_triggered:
            st.warning("🗑️ Session limit reached. Data cleaned. Please run `python setup_all.py` again.")
            st.stop()
        
        # Load RAG pipeline
        if st.session_state.rag_pipeline is None:
            try:
                st.session_state.rag_pipeline = RAGPipeline()
                st.session_state.setup_complete = True
            except Exception as e:
                st.error(f"❌ Error loading system: {e}")
                st.info("Please ensure you've run `python setup_all.py` first.")
                st.stop()

# Initialize on first run
if not st.session_state.setup_complete:
    initialize_system()

# Q&A Mode
if mode == "💬 Q&A Mode":
    st.header("💬 Ask Questions About Lung Cancer Research")
    
    # Example questions
    with st.expander("💡 Example Questions"):
        example_questions = [
            "What are the most effective treatments for lung cancer?",
            "What are the side effects of chemotherapy for lung cancer?",
            "How is lung cancer diagnosed?",
            "What is the survival rate for lung cancer?",
            "What are the risk factors for lung cancer?",
            "Compare immunotherapy and chemotherapy for lung cancer",
            "What are early warning signs of lung cancer?",
            "What is the role of targeted therapy in lung cancer treatment?"
        ]
        
        cols = st.columns(2)
        for idx, question in enumerate(example_questions):
            with cols[idx % 2]:
                if st.button(f"📌 {question}", key=f"ex_{idx}"):
                    st.session_state.current_question = question
    
    # Question input
    question = st.text_input(
        "Your Question:",
        value=st.session_state.get('current_question', ''),
        placeholder="e.g., What are common lung cancer treatments?"
    )
    
    # Ask button
    if st.button("🔍 Ask", type="primary"):
        if question:
            with st.spinner("🔍 Searching research papers..."):
                try:
                    result = st.session_state.rag_pipeline.answer_question(question)
                    
                    # Display answer
                    st.markdown("### 💡 Answer")
                    st.markdown(f'<div class="answer-box">{result["answer"]}</div>', 
                              unsafe_allow_html=True)
                    
                    # Display sources
                    st.markdown("### 📚 Sources")
                    with st.expander("📖 View Sources", expanded=True):
                        for idx, source in enumerate(result['sources'], 1):
                            st.markdown(f"""
                            <div class="source-box">
                                <strong>Source {idx}:</strong> {source['source']}<br>
                                <strong>Similarity:</strong> {source['similarity_score']:.2%}<br>
                                <strong>Text:</strong> {source['text'][:300]}...
                            </div>
                            """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ Please enter a question!")

# Summarization Mode
elif mode == "📄 Summarization Mode":
    st.header("📄 Document Summarization")
    
    # Get list of documents
    try:
        chunks = st.session_state.rag_pipeline.chunks
        unique_sources = sorted(set(chunk['source'] for chunk in chunks))
        
        # Document selector
        selected_doc = st.selectbox(
            "Select a research paper to summarize:",
            unique_sources
        )
        
        # Summarize button
        if st.button("📝 Generate Summary", type="primary"):
            with st.spinner("📝 Generating summary..."):
                try:
                    summary = st.session_state.rag_pipeline.summarize_document(selected_doc)
                    
                    st.markdown("### 📋 Summary")
                    st.markdown(f'<div class="answer-box">{summary}</div>', 
                              unsafe_allow_html=True)
                    
                    st.success("✅ Summary generated!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    except Exception as e:
        st.error(f"❌ Error loading documents: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🫁 Lung Cancer Research RAG Chatbot | Built with LangChain, FAISS & BioGPT</p>
    <p>By Suyash Kulkarni</p>
    <p style='font-size: 0.8rem;'>All answers are based on 5 research papers from PubMed</p>
</div>
""", unsafe_allow_html=True)