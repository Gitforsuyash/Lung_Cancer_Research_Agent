import json
import shutil
from pathlib import Path
from datetime import datetime
from config import *

class SessionManager:
    """Manages session tracking and automatic cleanup after 10 sessions"""
    
    def __init__(self):
        self.tracker_file = METADATA_DIR / "session_tracker.json"
        self.max_sessions = 10
        
    def initialize_tracker(self):
        """Create new session tracker file"""
        tracker_data = {
            "session_count": 0,
            "first_download": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_session": None,
            "total_papers": NUM_PAPERS,
            "auto_cleanup_enabled": True
        }
        
        with open(self.tracker_file, 'w') as f:
            json.dump(tracker_data, f, indent=2)
        
        return tracker_data
    
    def load_tracker(self):
        """Load session tracker data"""
        if not self.tracker_file.exists():
            return self.initialize_tracker()
        
        with open(self.tracker_file, 'r') as f:
            return json.load(f)
    
    def save_tracker(self, tracker_data):
        """Save session tracker data"""
        with open(self.tracker_file, 'w') as f:
            json.dump(tracker_data, f, indent=2)
    
    def increment_session(self):
        """Increment session count and check if cleanup needed"""
        tracker_data = self.load_tracker()
        tracker_data["session_count"] += 1
        tracker_data["last_session"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n📊 Session {tracker_data['session_count']}/{self.max_sessions}")
        
        # Check if cleanup needed
        if tracker_data["session_count"] >= self.max_sessions:
            print(f"\n⚠️  Maximum sessions ({self.max_sessions}) reached!")
            print("🗑️  Triggering automatic cleanup...")
            self.cleanup_all_data()
            return True  # Cleanup performed
        else:
            self.save_tracker(tracker_data)
            remaining = self.max_sessions - tracker_data["session_count"]
            print(f"✅ {remaining} sessions remaining before auto-cleanup")
            return False  # No cleanup
    
    def cleanup_all_data(self):
        """Delete all downloaded papers, processed data, and vectorstore"""
        print("\n" + "=" * 60)
        print("🗑️  CLEANING UP OLD DATA")
        print("=" * 60)
        
        directories_to_clean = [
            (PAPERS_DIR, "Research Papers"),
            (TEXTS_DIR, "Extracted Texts"),
            (CHUNKS_DIR, "Document Chunks"),
            (VECTORSTORE_DIR, "Vector Store"),
        ]
        
        for directory, name in directories_to_clean:
            if directory.exists():
                try:
                    shutil.rmtree(directory)
                    directory.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Cleaned: {name}")
                except Exception as e:
                    print(f"⚠️  Error cleaning {name}: {e}")
        
        # Reset session tracker
        self.initialize_tracker()
        
        print("\n" + "=" * 60)
        print("✅ CLEANUP COMPLETE!")
        print("=" * 60)
        print("\n💡 Next session will re-download papers and rebuild index.")
    
    def get_session_info(self):
        """Get current session information"""
        tracker_data = self.load_tracker()
        return {
            "current_session": tracker_data["session_count"],
            "max_sessions": self.max_sessions,
            "remaining_sessions": self.max_sessions - tracker_data["session_count"],
            "first_download": tracker_data.get("first_download", "Unknown"),
            "last_session": tracker_data.get("last_session", "Never"),
            "cleanup_needed": tracker_data["session_count"] >= self.max_sessions
        }
    
    def check_data_exists(self):
        """Check if all required data exists"""
        required_files = [
            FAISS_INDEX_PATH.with_suffix('.index'),
            FAISS_INDEX_PATH.with_suffix('.pkl'),
            CHUNKS_DIR / "all_chunks.json"
        ]
        
        required_dirs = [
            PAPERS_DIR,
            TEXTS_DIR
        ]
        
        # Check files exist
        files_exist = all(f.exists() for f in required_files)
        
        # Check directories have content
        dirs_have_content = all(
            d.exists() and any(d.iterdir()) 
            for d in required_dirs
        )
        
        return files_exist and dirs_have_content
    
    def force_cleanup(self):
        """Manually trigger cleanup (for admin use)"""
        print("\n⚠️  Manual cleanup triggered!")
        self.cleanup_all_data()
    
    def reset_counter(self):
        """Reset session counter without deleting data"""
        tracker_data = self.load_tracker()
        tracker_data["session_count"] = 0
        tracker_data["last_session"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_tracker(tracker_data)
        print("✅ Session counter reset to 0")


# Utility functions
def check_and_setup():
    """Check if setup needed and return status"""
    session_mgr = SessionManager()
    
    # Check if data exists
    data_exists = session_mgr.check_data_exists()
    
    if not data_exists:
        print("\n📦 No existing data found. Setup required.")
        return False, session_mgr
    else:
        print("\n✅ Existing data found. Loading from cache...")
        return True, session_mgr


if __name__ == "__main__":
    # Test session manager
    print("=" * 60)
    print("🧪 TESTING SESSION MANAGER")
    print("=" * 60)
    
    mgr = SessionManager()
    
    # Show current info
    info = mgr.get_session_info()
    print(f"\n📊 Current Session Info:")
    print(f"   Session: {info['current_session']}/{info['max_sessions']}")
    print(f"   Remaining: {info['remaining_sessions']}")
    print(f"   First Download: {info['first_download']}")
    print(f"   Last Session: {info['last_session']}")
    
    # Check data
    data_exists = mgr.check_data_exists()
    print(f"\n📁 Data exists: {data_exists}")
    
    # Simulate session increment
    print("\n🔄 Simulating session increment...")
    cleanup_triggered = mgr.increment_session()
    
    if cleanup_triggered:
        print("\n🗑️  Cleanup was triggered!")
    else:
        print("\n✅ Session incremented, no cleanup needed yet.")