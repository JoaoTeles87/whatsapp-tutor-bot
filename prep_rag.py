"""
Script to prepare RAG index from school documents
"""
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

def create_rag_index():
    """Create FAISS index from documents"""
    print("📚 Loading documents from ./documentos_escola...")
    
    # Load documents
    loader = DirectoryLoader(
        "./documentos_escola",
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    print(f"✅ Loaded {len(documents)} documents")
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    splits = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(splits)} chunks")
    
    # Create embeddings
    print("🔄 Creating embeddings...")
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("LLM_API_KEY")
    )
    
    # Create FAISS index
    vectorstore = FAISS.from_documents(splits, embeddings)
    
    # Save index
    vectorstore.save_local("./faiss_index")
    print("✅ FAISS index saved to ./faiss_index")
    print("🎉 RAG preparation complete!")

if __name__ == "__main__":
    create_rag_index()
