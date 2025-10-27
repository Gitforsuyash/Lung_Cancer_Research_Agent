#!/usr/bin/env python3
"""
Complete setup script for Lung Cancer RAG Chatbot
Runs all steps in order with session management
"""

import sys
import subprocess
import time
from session_manager import SessionManager

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def run_step(step_num, step_name, script_name):
    """Run a setup step"""
    print_header(f"STEP {step_num}: {step_name}")
    
    try:
        # Import and run the script
        print(f"▶️  Running {script_name}...\n")
        
        if script_name == "download_papers_arxiv.py":
            import download_papers_arxiv
            download_papers_arxiv.main()
        elif script_name == "extract_text.py":
            import extract_text
            extract_text.process_all_pdfs()
        elif script_name == "chunk_documents.py":
            import chunk_documents
            chunk_documents.process_all_texts()
        elif script_name == "create_vectorstore.py":
            import create_vectorstore
            create_vectorstore.main()
        
        print(f"\n✅ Step {step_num} completed successfully!")
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"\n❌ Error in step {step_num}: {e}")
        print(f"   Please check the error and try running {script_name} manually.")
        return False

def check_requirements():
    """Check if all requirements are installed"""
    print_header("CHECKING REQUIREMENTS")
    
    try:
        import Bio
        import requests
        import PyPDF2
        import langchain
        import faiss
        import sentence_transformers
        import transformers
        import streamlit
        
        print("✅ All required packages are installed!")
        return True
        
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("\n📦 Please install requirements first:")
        print("   pip install -r requirements.txt")
        return False

def main():
    """Main setup function"""
    print("\n" + "🫁" * 35)
    print("\n   LUNG CANCER RAG CHATBOT - COMPLETE SETUP")
    print("\n" + "🫁" * 35)
    
    # Initialize session manager
    session_mgr = SessionManager()
    
    # Check if cleanup needed
    session_info = session_mgr.get_session_info()
    if session_info['cleanup_needed']:
        print("\n⚠️  Previous session limit reached. Performing cleanup...")
        session_mgr.cleanup_all_data()
    
    # Check if data already exists
    if session_mgr.check_data_exists():
        print("\n✅ Existing data found!")
        print("   You can use the chatbot without re-downloading.")
        
        response = input("\n❓ Do you want to re-download anyway? (y/N): ")
        if response.lower() != 'y':
            print("\n✅ Using existing data. Run: streamlit run app.py")
            return
        else:
            print("\n🗑️  Cleaning existing data...")
            session_mgr.cleanup_all_data()
    
    print("\n📋 This script will:")
    print("   1. Download 10 research papers from PubMed")
    print("   2. Extract text from PDFs")
    print("   3. Chunk documents into smaller pieces")
    print("   4. Create embeddings and FAISS vector store")
    print("   5. Initialize session tracker (10 sessions)")
    print("\n⏱️  Estimated time: 20-30 minutes")
    print("\n" + "-" * 70)
    
    input("\n▶️  Press ENTER to start setup...")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Track start time
    start_time = time.time()
    
    # Run all steps
    steps = [
        (1, "Downloading Papers from PubMed", "download_papers_arxiv.py"),
        (2, "Extracting Text from PDFs", "extract_text.py"),
        (3, "Chunking Documents", "chunk_documents.py"),
        (4, "Creating Vector Store with FAISS", "create_vectorstore.py")
    ]
    
    for step_num, step_name, script_name in steps:
        success = run_step(step_num, step_name, script_name)
        if not success:
            print("\n❌ Setup failed. Please fix the error and try again.")
            sys.exit(1)
    
    # Initialize session tracker
    print_header("STEP 5: Initializing Session Tracker")
    session_mgr.initialize_tracker()
    print("✅ Session tracker initialized!")
    print(f"   → Configured for {session_mgr.max_sessions} sessions")
    print("   → Auto-cleanup enabled")
    
    # Calculate total time
    total_time = time.time() - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    
    # Final summary
    print_header("🎉 SETUP COMPLETE!")
    
    print(f"✅ All steps completed successfully!")
    print(f"⏱️  Total time: {minutes}m {seconds}s")
    print("\n📊 Summary:")
    print("   ✅ 10 research papers downloaded")
    print("   ✅ Text extracted from all PDFs")
    print("   ✅ Documents chunked for processing")
    print("   ✅ Vector store created with FAISS")
    print("   ✅ Embeddings generated with BiomedBERT")
    print("   ✅ Session tracker initialized (10 sessions)")
    
    print("\n🚀 Next Steps:")
    print("   1. Run the chatbot:")
    print("      streamlit run app.py")
    print("\n   2. Open your browser at:")
    print("      http://localhost:8501")
    
    print("\n📌 Session Management:")
    print(f"   • You can use the chatbot for {session_mgr.max_sessions} sessions")
    print("   • After 10 sessions, data auto-cleans")
    print("   • Next run will re-download papers")
    
    print("\n" + "=" * 70)
    print("💡 TIP: Check the sidebar in the app for session info!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()