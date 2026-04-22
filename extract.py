
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import glob
import os
from langchain_community.document_loaders import UnstructuredEPubLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma # (Or langchain_community.vectorstores depending on your version)

embeddings = HuggingFaceEmbeddings(
    model_name = "all-MiniLM-L6-v2",
    
)

db_directory = "ChromaDB/chroma_db"

epub_files = glob.glob("Data/*.epub")

if not epub_files:
    print("No files found")
    exit()

all_documents = []

for file_path in epub_files:
    try:
        loader = UnstructuredEPubLoader(file_path)
        documents = loader.load()
        
        all_documents.extend(documents)
        
    except Exception as e:
        print(f"Failed to ingest {file_path}. Skipping. Error: {e}")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 2000,
    chunk_overlap = 400,
    length_function = len,
    is_separator_regex = False
)

chunks = text_splitter.split_documents(all_documents)

if chunks:
    print(chunks[0].page_content)

vectorstore = Chroma.from_documents(
    documents = chunks,
    embedding = embeddings,
    persist_directory = db_directory
)