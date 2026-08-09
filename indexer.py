import os
import pickle
import faiss
from pathlib import Path
from engine import VisualMemoryEngine, ImageIndex

def get_smart_folders():
    """Automatically finds the user's standard media folders."""
    home = str(Path.home()) 
    target_folders = [
        os.path.join(home, "Pictures"),
        os.path.join(home, "Desktop"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "Documents")
    ]
    return [f for f in target_folders if os.path.exists(f)]

def build_index(folders_to_scan, save_path="index_data"):
    """
    Scans the provided list of folders, embeds the images, 
    and saves the FAISS index to disk.
    """
    print(f"Scanning folders: {folders_to_scan}")
    
    ai_engine = VisualMemoryEngine()
    db_index = ImageIndex()
    valid_exts = {'.png', '.jpg', '.jpeg', '.webp'}
    
    for folder in folders_to_scan:
        if not os.path.exists(folder):
            print(f"Skipping {folder} - Path does not exist.")
            continue
            
        for root, _, files in os.walk(folder):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in valid_exts:
                    full_path = os.path.join(root, file)
                    try:
                        emb = ai_engine.embed_image(full_path)
                        db_index.add_image(emb, full_path)
                        print(f"Indexed: {file}")
                    except Exception as e:
                        print(f"Failed to index {file}: {e}")

    # Save to disk
    os.makedirs(save_path, exist_ok=True)
    faiss.write_index(db_index.index, f"{save_path}/vector.index")
    with open(f"{save_path}/paths.pkl", "wb") as f:
        pickle.dump(db_index.image_paths, f)
        
    print(f"Indexing complete! {len(db_index.image_paths)} images saved.")
    return len(db_index.image_paths)

if __name__ == "__main__":
    # If run from terminal, just use the smart folders
    folders = get_smart_folders()
    build_index(folders)