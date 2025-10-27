import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from config import *

def load_chunks():
    """Load all chunks from JSON file"""
    chunks_file = CHUNKS_DIR / "all_chunks.json"
    
    if not chunks_file.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_file}\nPlease run chunk_documents.py first.")
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    return chunks

def create_embeddings(chunks, model_name=EMBEDDING_MODEL):
    """Create embeddings for all chunks using biomedical BERT"""
    print(f"🤖 Loading embedding model: {model_name}")
    print("   (This may take a few minutes on first run...)")
    
    # Load the biomedical BERT model
    model = SentenceTransformer(model_name)
    
    print(f"\n🔄 Generating embeddings for {len(chunks)} chunks...")
    print("   This may take 5-10 minutes depending on your hardware...")
    
    # Extract text from chunks
    texts = [chunk['text'] for chunk in chunks]
    
    # Generate embeddings in batches
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    print(f"✅ Generated embeddings with shape: {embeddings.shape}")
    
    return embeddings, model

def create_faiss_index(embeddings):
    """Create FAISS index for fast similarity search"""
    print(f"\n🗄️  Creating FAISS index...")
    
    # Get embedding dimension
    dimension = embeddings.shape[1]
    
    # Create FAISS index (using L2 distance)
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to index
    index.add(embeddings.astype('float32'))
    
    print(f"✅ FAISS index created with {index.ntotal} vectors")
    
    return index

def save_vectorstore(index, chunks):
    """Save FAISS index and chunks metadata"""
    print(f"\n💾 Saving vector store...")
    
    # Save FAISS index
    index_file = FAISS_INDEX_PATH.with_suffix('.index')
    faiss.write_index(index, str(index_file))
    print(f"   ✅ FAISS index saved: {index_file}")
    
    # Save chunks metadata
    metadata_file = FAISS_INDEX_PATH.with_suffix('.pkl')
    with open(metadata_file, 'wb') as f:
        pickle.dump(chunks, f)
    print(f"   ✅ Metadata saved: {metadata_file}")
    
    return index_file, metadata_file

def main():
    """Main function to create vector store"""
    print("=" * 60)
    print("🧮 CREATING VECTOR STORE WITH FAISS")
    print("=" * 60)
    
    try:
        # Load chunks
        print("\n📚 Loading chunks...")
        chunks = load_chunks()
        print(f"✅ Loaded {len(chunks)} chunks")
        
        # Create embeddings
        embeddings, model = create_embeddings(chunks)
        
        # Create FAISS index
        index = create_faiss_index(embeddings)
        
        # Save everything
        index_file, metadata_file = save_vectorstore(index, chunks)
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ VECTOR STORE CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Embedding dimension: {embeddings.shape[1]}")
        print(f"   Index size: {index.ntotal} vectors")
        print(f"   Model used: {EMBEDDING_MODEL}")
        print(f"\n📁 Files created:")
        print(f"   {index_file}")
        print(f"   {metadata_file}")
        print("\n🚀 Ready to use! Run: streamlit run app.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("   Make sure you've run the previous steps:")
        print("   1. download_papers.py")
        print("   2. extract_text.py")
        print("   3. chunk_documents.py")

if __name__ == "__main__":
    main()