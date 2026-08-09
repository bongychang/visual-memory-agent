import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image

class VisualMemoryEngine:
    def __init__(self):
        # Automatically use GPU if you have one, otherwise fallback to CPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "openai/clip-vit-base-patch32"
        
        # Load the model and processor
        self.model = CLIPModel.from_pretrained(self.model_id).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(self.model_id)

    def embed_image(self, image_path):
        """Converts an image into a searchable vector."""
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            emb = self.model.get_image_features(**inputs)
        return emb.cpu().numpy().flatten()

    def embed_text(self, query):
        """Converts a text query into a vector in the same space."""
        inputs = self.processor(text=[query], return_tensors="pt", padding=True).to(self.device)
        
        with torch.no_grad():
            emb = self.model.get_text_features(**inputs)
        return emb.cpu().numpy().flatten()

import faiss
import numpy as np

class ImageIndex:
    def __init__(self, vector_dim=512):
        # IndexFlatIP calculates the Inner Product. 
        # When vectors are normalized, Inner Product equals Cosine Similarity.
        self.index = faiss.IndexFlatIP(vector_dim) 
        self.image_paths = []
        
    def add_image(self, embedding, path):
        # Normalize the vector before adding it
        emb_reshaped = embedding.reshape(1, -1)
        faiss.normalize_L2(emb_reshaped)
        
        self.index.add(emb_reshaped)
        self.image_paths.append(path)
        
    def search(self, query_embedding, k=5):
        # Normalize the search query
        query_reshaped = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_reshaped)
        
        # Search the index for the top 'k' closest matches
        distances, indices = self.index.search(query_reshaped, k)
    
    def load(self, save_path="index_data"):
        import faiss
        import pickle
        # Load the FAISS index
        self.index = faiss.read_index(f"{save_path}/vector.index")
        
        # Load the file paths
        with open(f"{save_path}/paths.pkl", "rb") as f:
            self.image_paths = pickle.load(f)

        results = []
        for j, i in enumerate(indices[0]):
            if i != -1: # FAISS returns -1 if there aren't enough images
                results.append((self.image_paths[i], distances[0][j]))
        return results