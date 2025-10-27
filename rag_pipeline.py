import pickle
import faiss
import numpy as np
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
from config import *

class RAGPipeline:
    """RAG Pipeline for Question Answering with Small Cached Model"""
    
    def __init__(self):
        """Initialize the RAG pipeline"""
        self.embedding_model = None
        self.index = None
        self.chunks = None
        self.llm_pipeline = None
        
        self.load_vectorstore()
        self.load_models()
    
    def load_vectorstore(self):
        """Load FAISS index and chunks"""
        print("📚 Loading vector store...")
        
        index_file = FAISS_INDEX_PATH.with_suffix('.index')
        metadata_file = FAISS_INDEX_PATH.with_suffix('.pkl')
        
        if not index_file.exists() or not metadata_file.exists():
            raise FileNotFoundError(
                "Vector store not found! Please run create_vectorstore.py first."
            )
        
        # Load FAISS index
        self.index = faiss.read_index(str(index_file))
        
        # Load chunks metadata
        with open(metadata_file, 'rb') as f:
            self.chunks = pickle.load(f)
        
        print(f"✅ Loaded {len(self.chunks)} chunks")
    
    def check_model_cached(self, model_name):
        """Check if model is already cached locally"""
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        
        # Clean model name for directory check
        model_dir_name = model_name.replace("/", "--")
        
        # Check if any directory contains this model
        if cache_dir.exists():
            for item in cache_dir.iterdir():
                if model_dir_name in item.name:
                    print(f"✅ Model already cached: {model_name}")
                    return True
        
        print(f"📥 Model not cached, will download: {model_name}")
        return False
    
    def load_models(self):
        """Load embedding and small LLM models with caching check"""
        print("🤖 Loading models...")
        
        # Load embedding model (same as used for creating vectors)
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        if self.check_model_cached(EMBEDDING_MODEL):
            print("   Using cached version...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ Loaded embedding model")
        
        # Load SMALL LLM for text generation
        # Using FLAN-T5 Small (77MB) - Perfect for your needs!
        small_model_name = "google/flan-t5-small"  # Only 77MB!
        
        try:
            print(f"\n🧠 Loading LLM: {small_model_name}")
            print(f"   Model size: ~77MB (very small!)")
            
            if self.check_model_cached(small_model_name):
                print("   Using cached version (no download needed)...")
            else:
                print("   Downloading for first time (this will be cached)...")
            
            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(small_model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(small_model_name)
            
            # Create pipeline
            self.llm_pipeline = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=256,
                device=0 if torch.cuda.is_available() else -1
            )
            
            print(f"✅ Loaded LLM: {small_model_name}")
            print(f"   Location: Cached in ~/.cache/huggingface/")
            
        except Exception as e:
            print(f"⚠️  Could not load {small_model_name}: {e}")
            print("   Falling back to extractive answers only...")
            self.llm_pipeline = None
    
    def retrieve_relevant_chunks(self, query, top_k=TOP_K_RETRIEVAL):
        """Retrieve most relevant chunks for a query"""
        # Create embedding for query
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Get relevant chunks
        relevant_chunks = []
        for idx, distance in zip(indices[0], distances[0]):
            chunk = self.chunks[idx].copy()
            chunk['similarity_score'] = float(1 / (1 + distance))
            relevant_chunks.append(chunk)
        
        return relevant_chunks
    
    def generate_answer(self, query, context):
        """Generate answer using small LLM or extractive method"""
        
        if self.llm_pipeline:
            # Use FLAN-T5 for generation
            prompt = f"""Answer the question based on the context and check answer is relevant to question if it is then show answer if it is not then search all over the internet and find best possible answer for it from your knowledge.

Context: {context[:800]}

Question: {query}

Answer:"""
            
            try:
                result = self.llm_pipeline(
                    prompt,
                    max_length=200,
                    num_return_sequences=50,
                    temperature=0.7,
                    do_sample=True
                )
                
                answer = result[0]['generated_text'].strip()
                
                if answer and len(answer) > 10:
                    return answer
                else:
                    # Fallback to extractive
                    return self.generate_extractive_answer(query, context)
                    
            except Exception as e:
                print(f"⚠️ Generation error: {e}")
                return self.generate_extractive_answer(query, context)
        else:
            # Use extractive method
            return self.generate_extractive_answer(query, context)
    
    def generate_extractive_answer(self, query, context):
        """Generate answer by extracting most relevant sentences"""
        sentences = context.split('. ')
        
        # Get query embedding
        query_emb = self.embedding_model.encode([query])
        
        # Score sentences
        sentence_scores = []
        for sent in sentences[:15]:
            if len(sent.strip()) > 20:
                sent_emb = self.embedding_model.encode([sent])
                similarity = np.dot(query_emb[0], sent_emb[0]) / (
                    np.linalg.norm(query_emb[0]) * np.linalg.norm(sent_emb[0])
                )
                sentence_scores.append((sent, similarity))
        
        # Sort by score
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 3 sentences
        answer = '. '.join([s[0] for s in sentence_scores[:3]]) + '.'
        
        return answer
    
    def answer_question(self, query):
        """Complete RAG pipeline: retrieve + generate"""
        print(f"\n🔍 Query: {query}")
        
        # Retrieve relevant chunks
        print("📚 Retrieving relevant information...")
        relevant_chunks = self.retrieve_relevant_chunks(query)
        
        # Combine context
        context = "\n\n".join([
            f"[Source: {chunk['source']}]\n{chunk['text']}"
            for chunk in relevant_chunks
        ])
        
        print(f"✅ Found {len(relevant_chunks)} relevant chunks")
        
        # Generate answer
        print("🤖 Generating answer...")
        answer = self.generate_answer(query, context)
        
        return {
            'answer': answer,
            'sources': relevant_chunks,
            'context': context
        }
    
    def summarize_document(self, source_file):
        """Summarize a specific document"""
        # Get all chunks from this document
        doc_chunks = [c for c in self.chunks if c['source'] == source_file]
        
        if not doc_chunks:
            return f"Document '{source_file}' not found."
        
        # Combine chunks
        full_text = " ".join([c['text'] for c in doc_chunks[:5]])
        
        if self.llm_pipeline:
            # Use LLM for summarization
            prompt = f"Summarize this lung cancer research in 3-4 sentences:\n\n{full_text[:1000]}"
            
            try:
                result = self.llm_pipeline(
                    prompt,
                    max_length=150,
                    num_return_sequences=100
                )
                return result[0]['generated_text'].strip()
            except:
                pass
        
        # Fallback: Extract key sentences
        key_points = []
        for chunk in doc_chunks[:5]:
            sentences = [s.strip() for s in chunk['text'].split('.') if len(s.strip()) > 30]
            if sentences:
                key_points.append(sentences[0])
        
        summary = "Key findings: " + ". ".join(key_points[:4]) + "."
        return summary
    
    def get_model_info(self):
        """Get information about loaded models"""
        info = {
            'embedding_model': EMBEDDING_MODEL,
            'llm_model': 'google/flan-t5-small (77MB)',
            'llm_loaded': self.llm_pipeline is not None,
            'cache_location': str(Path.home() / ".cache" / "huggingface"),
            'models_cached': True
        }
        return info

# Test the pipeline
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING RAG PIPELINE")
    print("=" * 60)
    
    try:
        # Initialize pipeline
        rag = RAGPipeline()
        
        # Show model info
        print("\n" + "=" * 60)
        print("📊 MODEL INFORMATION:")
        print("=" * 60)
        info = rag.get_model_info()
        for key, value in info.items():
            print(f"{key}: {value}")
        
        # Test question
        test_query = "What are the common treatments for lung cancer?"
        result = rag.answer_question(test_query)
        
        print("\n" + "=" * 60)
        print("📝 ANSWER:")
        print("=" * 60)
        print(result['answer'])
        print("\n" + "=" * 60)
        print("📚 SOURCES:")
        print("=" * 60)
        for source in result['sources']:
            print(f"- {source['source']} (Similarity: {source['similarity_score']:.2f})")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()