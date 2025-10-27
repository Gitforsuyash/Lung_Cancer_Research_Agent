import os
import PyPDF2
from pathlib import Path
from config import *

def extract_text_from_pdf(pdf_path):
    """Extract text from a single PDF file"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
        
        return text.strip()
    
    except Exception as e:
        print(f"❌ Error extracting text from {pdf_path.name}: {e}")
        return ""

def clean_text(text):
    """Clean extracted text"""
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove common PDF artifacts
    text = text.replace('\x00', '')
    
    return text

def process_all_pdfs():
    """Process all PDFs in the research_papers directory"""
    print("=" * 60)
    print("📄 TEXT EXTRACTION FROM PDFs")
    print("=" * 60)
    
    pdf_files = list(PAPERS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in research_papers directory!")
        print("   Please run download_papers.py first.")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files\n")
    
    extracted_count = 0
    
    for idx, pdf_path in enumerate(pdf_files, 1):
        print(f"[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
        
        # Extract text
        text = extract_text_from_pdf(pdf_path)
        
        if text:
            # Clean text
            text = clean_text(text)
            
            # Save extracted text
            text_filename = pdf_path.stem + ".txt"
            text_path = TEXTS_DIR / text_filename
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"   ✅ Extracted {len(text)} characters")
            print(f"   💾 Saved to: {text_filename}")
            extracted_count += 1
        else:
            print(f"   ⚠️  No text extracted")
        
        print()
    
    print("=" * 60)
    print(f"✅ Successfully extracted text from {extracted_count} papers!")
    print(f"📁 Location: {TEXTS_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    process_all_pdfs()