import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import *

def chunk_text(text, source_file):
    """Split text into chunks with metadata"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    # Add metadata to each chunk
    chunks_with_metadata = []
    for idx, chunk in enumerate(chunks):
        chunks_with_metadata.append({
            "text": chunk,
            "source": source_file,
            "chunk_id": idx
        })
    
    return chunks_with_metadata

def process_all_texts():
    """Process all extracted text files"""
    print("=" * 60)
    print("✂️  TEXT CHUNKING")
    print("=" * 60)
    
    text_files = list(TEXTS_DIR.glob("*.txt"))
    
    if not text_files:
        print("❌ No text files found!")
        print("   Please run extract_text.py first.")
        return
    
    print(f"📚 Found {len(text_files)} text files\n")
    
    all_chunks = []
    
    for idx, text_path in enumerate(text_files, 1):
        print(f"[{idx}/{len(text_files)}] Processing: {text_path.name}")
        
        # Read text
        with open(text_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Create chunks
        chunks = chunk_text(text, text_path.name)
        all_chunks.extend(chunks)
        
        print(f"   ✅ Created {len(chunks)} chunks")
    
    # Save all chunks
    chunks_file = CHUNKS_DIR / "all_chunks.json"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✅ Total chunks created: {len(all_chunks)}")
    print(f"💾 Saved to: {chunks_file}")
    print("=" * 60)
    
    # Statistics
    avg_chunk_size = sum(len(c['text']) for c in all_chunks) / len(all_chunks)
    print(f"\n📊 Statistics:")
    print(f"   Average chunk size: {avg_chunk_size:.0f} characters")
    print(f"   Chunk size range: {CHUNK_SIZE} ± {CHUNK_OVERLAP}")

if __name__ == "__main__":
    process_all_texts()