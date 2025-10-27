import os
import time
import json
import requests
import arxiv
from config import *

def search_arxiv(query, num_results=20):
    """Search arXiv for lung cancer papers"""
    print(f"🔍 Searching arXiv for: '{query}'...")
    
    # Search arXiv
    search = arxiv.Search(
        query=f"{query} lung cancer biology medicine",
        max_results=num_results * 2,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    results = list(search.results())
    print(f"✅ Found {len(results)} papers")
    return results

def download_arxiv_paper(paper, filename, paper_num):
    """Download paper from arXiv"""
    try:
        print(f"\n[{paper_num}] Downloading: {paper.title[:60]}...")
        
        # Download PDF
        pdf_url = paper.pdf_url
        response = requests.get(pdf_url, timeout=30)
        
        if response.status_code == 200:
            filepath = PAPERS_DIR / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Saved: {filename}")
            return True
        else:
            print(f"❌ Download failed (status {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function to download papers from arXiv"""
    print("=" * 60)
    print("🫁 LUNG CANCER RESEARCH PAPER DOWNLOADER (arXiv)")
    print("=" * 60)
    
    # Search arXiv
    papers = search_arxiv("lung cancer treatment", NUM_PAPERS)
    
    if not papers:
        print("❌ No papers found!")
        return
    
    print(f"\n🎯 Downloading {NUM_PAPERS} papers...\n")
    
    # Download papers
    downloaded = 0
    metadata_list = []
    
    for idx, paper in enumerate(papers):
        if downloaded >= NUM_PAPERS:
            break
        
        # Clean title for filename
        clean_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_'))
        clean_title = clean_title[:60].strip()
        
        filename = f"paper_{downloaded + 1}_{clean_title}.pdf"
        filename = filename.replace(" ", "_")
        
        # Download
        if download_arxiv_paper(paper, filename, downloaded + 1):
            metadata = {
                "arxiv_id": paper.entry_id,
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "published": str(paper.published),
                "filename": filename,
                "download_date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            metadata_list.append(metadata)
            downloaded += 1
        
        time.sleep(1)  # Be nice to arXiv
    
    # Save metadata
    if metadata_list:
        metadata_file = METADATA_DIR / "papers_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata_list, f, indent=2)
    
    print("\n" + "=" * 60)
    if downloaded > 0:
        print(f"✅ Successfully downloaded {downloaded} papers!")
        print(f"📁 Location: {PAPERS_DIR}")
        print(f"📋 Metadata: {metadata_file}")
    else:
        print("❌ No papers could be downloaded!")
    print("=" * 60)

if __name__ == "__main__":
    # Install arxiv package first: pip install arxiv
    try:
        import arxiv
        main()
    except ImportError:
        print("❌ Please install arxiv package:")
        print("   pip install arxiv")