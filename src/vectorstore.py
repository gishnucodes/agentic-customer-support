from dotenv import load_dotenv
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import requests
import re
from config import  Config as cfg

load_dotenv()

def retrieve_policy(url:str):
    response = requests.get(url)
    response.raise_for_status()
    faq_text = response.text
    docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]
    return docs

def get_vector_retriever(documents):
    # Initialize Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    # Split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    # texts = text_splitter.split_texts(documents)
    docstest = text_splitter.create_documents(documents)
    # Create the vector store
    vectorstore = FAISS.from_documents(docstest, embeddings)
    # Create the retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    return retriever

def load_policy():
    policy = retrieve_policy(cfg.POLICY_URL)
    vector_retriever = get_vector_retriever(policy)
    return vector_retriever