"""
RAG Service for retrieving school documents
"""
import logging
import os
from typing import Optional
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)


class RAGService:
    """Service for retrieving relevant documents"""
    
    def __init__(self, api_key: str, index_path: str = "./faiss_index"):
        """
        Initialize RAG service
        
        Args:
            api_key: Not used (kept for compatibility)
            index_path: Path to FAISS index
        """
        self.index_path = index_path
        self.vectorstore = None
        
        try:
            if os.path.exists(index_path):
                # Use HuggingFace embeddings (free and local)
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                self.vectorstore = FAISS.load_local(
                    index_path,
                    embeddings,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"RAG index loaded from {index_path}")
            else:
                logger.warning(f"RAG index not found at {index_path}. Run prep_rag.py first.")
        except Exception as e:
            logger.error(f"Error loading RAG index: {e}")
    
    def search(self, query: str, k: int = 3) -> Optional[str]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            Concatenated relevant documents or None
        """
        if not self.vectorstore:
            return None
        
        try:
            docs = self.vectorstore.similarity_search(query, k=k)
            if docs:
                context = "\n\n".join([doc.page_content for doc in docs])
                logger.info(f"Found {len(docs)} relevant documents for query: {query[:50]}...")
                return context
            return None
        except Exception as e:
            logger.error(f"Error searching RAG: {e}")
            return None
