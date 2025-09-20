from app.extensions import celery, db
from app.models import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader # For .txt files
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os

# Define where to save the vector stores (the "digital brains")
VECTOR_STORE_DIR = "vector_stores"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

@celery.task
def process_document(document_id):
    """
    The real background task to process a document:
    1. Load the document content.
    2. Split it into chunks.
    3. Create vector embeddings.
    4. Save it to a FAISS vector store specific to the agent.
    """
    print(f"Starting REAL processing for document ID: {document_id}")
    doc = Document.query.get(document_id)
    if not doc:
        print(f"Error: Document with ID {document_id} not found.")
        return

    try:
        doc.status = 'Processing'
        db.session.commit()

        # 1. Load the document using LangChain's loader
        loader = TextLoader(doc.filepath, encoding='utf-8')
        documents = loader.load()

        # 2. Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        print(f"Document split into {len(chunks)} chunks.")

        # 3. Create embeddings
        # This uses a powerful open-source model. It will download the model the first time.
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 4. Save to FAISS vector store
        agent_vector_store_path = os.path.join(VECTOR_STORE_DIR, f"agent_{doc.agent_id}")
        
        if os.path.exists(agent_vector_store_path):
            # If a store already exists for this agent, load it and add to it
            vector_store = FAISS.load_local(agent_vector_store_path, embeddings, allow_dangerous_deserialization=True)
            vector_store.add_documents(chunks)
            print("Added new document chunks to existing agent vector store.")
        else:
            # If it's the first document for this agent, create a new store
            vector_store = FAISS.from_documents(chunks, embeddings)
            print("Created a new vector store for this agent.")

        vector_store.save_local(agent_vector_store_path)

        doc.status = 'Complete'
        db.session.commit()
        print(f"SUCCESS: Document {doc.filename} has been processed and embedded.")
        return f"Document {doc.id} embedded successfully."

    except Exception as e:
        print(f"ERROR processing document {doc.id}: {str(e)}")
        doc.status = 'Error'
        db.session.commit()
        return f"Error processing document {doc.id}."

# from app.extensions import celery, db
# from app.models import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import FAISS
# from langchain_community.embeddings import HuggingFaceEmbeddings
# import os

# # Define where to save the vector stores
# VECTOR_STORE_DIR = "vector_stores"
# os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

# @celery.task
# def process_document(document_id):
#     """
#     The real background task to process a document:
#     1. Load the document content.
#     2. Split it into chunks.
#     3. Create vector embeddings.
#     4. Save it to a FAISS vector store specific to the agent.
#     """
#     print(f"Starting REAL processing for document ID: {document_id}")
#     doc = Document.query.get(document_id)
#     if not doc:
#         print(f"Error: Document with ID {document_id} not found.")
#         return

#     try:
#         doc.status = 'Processing'
#         db.session.commit()

#         # 1. Load the document
#         # Simple text loader for now, we'll add more later
#         with open(doc.filepath, 'r', encoding='utf-8') as f:
#             text = f.read()
        
#         documents_for_langchain = [text] # Langchain expects a list

#         # 2. Split into chunks
#         text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#         chunks = text_splitter.create_documents(documents_for_langchain)
#         print(f"Document split into {len(chunks)} chunks.")

#         # 3. Create embeddings
#         # This uses a powerful open-source model. It will download the model the first time.
#         embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
#         # 4. Save to FAISS vector store
#         agent_vector_store_path = os.path.join(VECTOR_STORE_DIR, f"agent_{doc.agent_id}")
        
#         if os.path.exists(agent_vector_store_path):
#             # If a store already exists for this agent, load it and add to it
#             vector_store = FAISS.load_local(agent_vector_store_path, embeddings, allow_dangerous_deserialization=True)
#             vector_store.add_documents(chunks)
#             print("Added new document chunks to existing agent vector store.")
#         else:
#             # If it's the first document for this agent, create a new store
#             vector_store = FAISS.from_documents(chunks, embeddings)
#             print("Created a new vector store for this agent.")

#         vector_store.save_local(agent_vector_store_path)

#         doc.status = 'Complete'
#         db.session.commit()
#         print(f"SUCCESS: Document {doc.filename} has been processed and embedded.")
#         return f"Document {doc.id} embedded successfully."

#     except Exception as e:
#         print(f"ERROR processing document {doc.id}: {str(e)}")
#         doc.status = 'Error'
#         db.session.commit()
#         return f"Error processing document {doc.id}."