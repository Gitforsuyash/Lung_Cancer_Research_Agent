import os
from pathlib import Path

# Base directories - HuggingFace compatible
BASE_DIR = Path(__file__).parent

# Use /tmp for HuggingFace Spaces, local otherwise
IS_HUGGINGFACE = os.getenv("SPACE_ID") is not None

if IS_HUGGINGFACE:
    WRITABLE_DIR = Path("/tmp/lung_cancer_rag")
    WRITABLE_DIR.mkdir(parents=True, exist_ok=True)
    PAPERS_DIR = WRITABLE_DIR / "research_papers"
    PROCESSED_DIR = WRITABLE_DIR / "processed_data"
    VECTORSTORE_DIR = WRITABLE_DIR / "vectorstore"
    METADATA_DIR = WRITABLE_DIR / "metadata"
else:
    PAPERS_DIR = BASE_DIR / "research_papers"
    PROCESSED_DIR = BASE_DIR / "processed_data"
    VECTORSTORE_DIR = BASE_DIR / "vectorstore"
    METADATA_DIR = BASE_DIR / "metadata"

TEXTS_DIR = PROCESSED_DIR / "extracted_texts"
CHUNKS_DIR = PROCESSED_DIR / "chunks"

# Create directories
for directory in [PAPERS_DIR, TEXTS_DIR, CHUNKS_DIR, VECTORSTORE_DIR, METADATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# PubMed settings
PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "research@example.com")
PUBMED_QUERY = "lung cancer treatment"
NUM_PAPERS = 5  # Reduced for faster HuggingFace deployment

# Chunking settings - Larger chunks for better context
CHUNK_SIZE = 1500  # Increased from 1000 for more context
CHUNK_OVERLAP = 300  # Increased overlap

# Embedding model - Fast and efficient
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # 22MB, fast
# Alternative for better medical: "dmis-lab/biobert-base-cased-v1.2" (420MB)

# LLM settings - Using better model for comprehensive answers
LLM_MODEL = "google/flan-t5-base"  # 250MB - Better quality than small
# Alternative: "google/flan-t5-large" (780MB) for even better answers

# FAISS settings
FAISS_INDEX_PATH = VECTORSTORE_DIR / "faiss_index"
TOP_K_RETRIEVAL = 5  # Increased from 3 for more context

# Generation settings - For comprehensive answers
MAX_ANSWER_LENGTH = 512  # Longer answers
MIN_ANSWER_LENGTH = 100  # Ensure substantial responses
TEMPERATURE = 0.7  # Balanced creativity/accuracy

# Streamlit settings
APP_TITLE = "Lung Cancer Research RAG Chatbot"
APP_ICON = "🫁"