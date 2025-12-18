import os
import yaml
import shutil
import datetime
import uuid
import pytz
import logging
import gradio as gr


from langchain_groq import ChatGroq

from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredExcelLoader,
    UnstructuredWordDocumentLoader,
)

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma



# ---------------------------------------
# CONFIG
# ---------------------------------------
IST = pytz.timezone("Asia/Kolkata")
LOG_FILE = f"{datetime.datetime.now(IST).strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_PATH = os.path.join("..", "logs")
os.makedirs(LOG_PATH, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_PATH, LOG_FILE),
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ---------------------------------------
# Embedding Model
# ---------------------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
)


# ---------------------------------------
# Helpers: Loaders
# ---------------------------------------
def load_docs(files):
    """Auto-detect loader based on file extension."""
    logging.info("Loading documents")

    loaders = {
        ".pdf": PyPDFLoader,
        ".xlsx": UnstructuredExcelLoader,
        ".docx": UnstructuredWordDocumentLoader,
    }

    docs = []
    for file in files:
        ext = os.path.splitext(file)[1]

        if ext not in loaders:
            raise gr.Error(f"Unsupported file: {ext}")

        loader = loaders[ext](file)
        loaded_docs = loader.load()
        docs.extend(loaded_docs)

        logging.info(f"Loaded {len(loaded_docs)} from {file}")

    return docs


# ---------------------------------------
# Text Splitter
# ---------------------------------------
def get_document_chunks(docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    logging.info(f"Split into {len(splits)} chunks")
    return splits


# ---------------------------------------
# Vector Store (Chroma)
# ---------------------------------------
def get_vector_store(splits, collection_name):
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_model,
        persist_directory="../chat_with_data",
        collection_name=collection_name,
    )
    logging.info("Vectorstore created")
    return vectorstore


def get_retriever(vs):
    return vs.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 7, "fetch_k": 20},
    )


# ---------------------------------------
# System Prompt
# ---------------------------------------
def read_system_prompt(file_name):
    with open(f"./system_prompt/{file_name}", "r") as f:
        return yaml.safe_load(f)


# ---------------------------------------
# RAG Chain (Modern LCEL)
# ---------------------------------------
def build_rag_chain(system_prompt, retriever):
    logging.info("Building modern RAG pipeline")

    llm = ChatGroq(model="llama-3.3-70b-versatile")

    template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Question: {question}\n\nContext: {context}"),
        ]
    )

    rag_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | template
        | llm
        | StrOutputParser()
    )

    return rag_chain


# ---------------------------------------
# File Save
# ---------------------------------------
def create_unique_filename():
    uid = uuid.uuid4()
    timestamp = datetime.datetime.now(IST).strftime("%d-%m-%Y-%H-%M-%S")
    return f"file-{uid}-{timestamp}"


def validate_and_save_files(uploaded_files):
    if not uploaded_files:
        raise gr.Error("Please upload files.")

    file_group_name = create_unique_filename()
    saved_files = []

    for idx, file in enumerate(uploaded_files, start=1):
        ext = os.path.splitext(file.name)[1]

        if ext not in [".pdf", ".docx", ".xlsx"]:
            raise gr.Error("Only PDF, DOCX, XLSX allowed.")

        save_path = os.path.join("../data", f"{file_group_name}-{idx}{ext}")
        shutil.copyfile(file.name, save_path)
        saved_files.append(save_path)

        logging.info(f"Saved {file.name} → {save_path}")

    return saved_files, file_group_name


# ---------------------------------------
# MAIN RAG PROCESSOR
# ---------------------------------------
def proceed_input(text, uploaded_files):
    saved_files, collection_name = validate_and_save_files(uploaded_files)

    docs = load_docs(saved_files)

    # Add user free text as document
    if text.strip():
        docs.append(Document(page_content=text))

    splits = get_document_chunks(docs)
    vectorstore = get_vector_store(splits, collection_name)
    retriever = get_retriever(vectorstore)
    system_prompt = read_system_prompt("custom.yaml")

    return build_rag_chain(system_prompt, retriever)


# ---------------------------------------
# ANSWER PROCESSING
# ---------------------------------------
def process_user_question(user_input, rag_chain):
    logging.info(f"User Q: {user_input}")
    answer = rag_chain.invoke(user_input)
    return answer
