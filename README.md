🫁 Lung Cancer Research RAG Chatbot
A Retrieval-Augmented Generation (RAG) chatbot that answers questions based on 10 lung cancer research papers from PubMed using FAISS and biomedical language models.

🎯 Features
Automatic Paper Download: Fetches 10 lung cancer research papers from PubMed automatically
Question Answering: Ask questions and get answers based on the research papers
Document Summarization: Generate summaries of individual papers
Source Citations: Shows which papers were used to generate answers
Biomedical Models: Uses CancerBERT/BiomedBERT for embeddings and BioGPT for generation
🏗️ Architecture
PubMed → PDF Download → Text Extraction → Chunking → Embeddings (BioBERT) → FAISS Index
                                                                                    ↓
User Query → Embedding → FAISS Search → Retrieve Context → LLM (BioGPT) → Answer
📦 Tech Stack
Component	Technology
PDF Download	Biopython, Requests
PDF Parsing	PyPDF2
Text Chunking	LangChain
Embeddings	BioBERT / BiomedBERT
Vector Store	FAISS
LLM	BioGPT
Framework	LangChain
UI	Streamlit
🚀 Quick Start
1. Clone and Setup
bash
# Create project directory
mkdir lung_cancer_rag
cd lung_cancer_rag

# Install requirements
pip install -r requirements.txt
2. Configure
Edit .env file:

bash
PUBMED_EMAIL=your_email@example.com
HF_API_TOKEN=your_huggingface_token  # Optional
3. Run Complete Setup
Option A: Automatic (Recommended)

bash
python setup_all.py
Option B: Manual Step-by-Step

bash
# Step 1: Download papers
python download_papers.py

# Step 2: Extract text
python extract_text.py

# Step 3: Chunk documents
python chunk_documents.py

# Step 4: Create vector store
python create_vectorstore.py
4. Launch Chatbot
bash
streamlit run app.py
Open browser at: http://localhost:8501

📁 Project Structure
lung_cancer_rag/
├── config.py                    # Configuration settings
├── download_papers_arxiv.py           # PubMed paper downloader
├── extract_text.py              # PDF text extraction
├── chunk_documents.py           # Text chunking
├── create_vectorstore.py        # FAISS index creation
├── rag_pipeline.py              # RAG Q&A system
├── app.py                       # Streamlit UI
├── setup_all.py                 # Complete setup automation
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
│
├── research_papers/             # Downloaded PDFs
├── processed_data/              # Extracted text & chunks
├── vectorstore/                 # FAISS index files
└── metadata/                    # Paper metadata
💡 Usage
Q&A Mode
Select "💬 Q&A Mode" in sidebar
Enter your question or click example questions
Get answer with source citations
Example questions:

"What are the most effective treatments for lung cancer?"
"What are the side effects of immunotherapy?"
"How is lung cancer diagnosed?"
Summarization Mode
Select "📄 Summarization Mode" in sidebar
Choose a paper from dropdown
Click "Generate Summary"
🔧 Customization
Change Number of Papers
Edit config.py:

python
NUM_PAPERS = 20  # Download 20 papers instead of 10
Change Search Query
Edit config.py:

python
PUBMED_QUERY = "lung cancer immunotherapy"
Change Embedding Model
Edit config.py:

python
EMBEDDING_MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
Change LLM Model
Edit config.py:

python
HF_MODEL = "stanford-crfm/BioMedLM"
🐛 Troubleshooting
Issue: "No PDF files found"
Solution: Run python download_papers_arxiv.py first

Issue: "Vector store not found"
Solution: Run python create_vectorstore.py

Issue: "Out of memory"
Solution: Reduce NUM_PAPERS in config.py or use smaller model

Issue: "PubMed API error"
Solution: Check your email in .env and internet connection

Issue: "Model download too slow"
Solution: Models are downloaded once and cached. Wait for first run.

📊 Performance
Setup Time: 20-30 minutes (one-time)
Query Response: 3-10 seconds
Storage: ~100-200 MB for 10 papers
GPU: Optional (CPU works fine, just slower)
🔐 Privacy
All papers stored locally
Only query text sent to HuggingFace API
No external web search
Data stays on your machine
📚 How It Works
Download: Automatically fetches open-access papers from PubMed Central
Extract: Converts PDFs to plain text
Chunk: Splits text into 1000-character chunks with 200-char overlap
Embed: Generates 768-dimensional vectors using BioBERT
Index: Stores vectors in FAISS for fast similarity search
Query: Converts question to vector, finds similar chunks
Generate: LLM generates answer based on retrieved context
🎓 Models Used
Embeddings: pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb
Fine-tuned BERT for biomedical text
768-dimensional embeddings
LLM: microsoft/BioGPT-Large
Pre-trained on biomedical literature
Generates domain-specific answers
📝 License
This project is for educational and research purposes.

🤝 Contributing
Feel free to submit issues and pull requests!

📧 Support
For issues:

Check existing error messages
Review troubleshooting section
Run individual scripts to isolate problems
🙏 Acknowledgments
PubMed/NCBI for research papers
HuggingFace for models
LangChain for RAG framework
FAISS for vector search
