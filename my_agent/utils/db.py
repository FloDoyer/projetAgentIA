import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

JOURNAL_DIR = "my_agent/journal"
DB_DIR = "my_agent/chroma_db"

def initialiser_memoire():
    loader = DirectoryLoader(JOURNAL_DIR, glob="./*.txt", loader_cls=TextLoader)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name="jinaai/jina-embeddings-v3",model_kwargs={"trust_remote_code": True})
    vectordb = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings, 
        persist_directory=DB_DIR
    )
    return vectordb

def chercher_dans_journal(requete):
    embeddings = HuggingFaceEmbeddings(model_name="jinaai/jina-embeddings-v3",model_kwargs={"trust_remote_code": True})
    vectordb = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    resultats = vectordb.similarity_search(requete, k=3)
    return "\n\n".join([doc.page_content for doc in resultats])