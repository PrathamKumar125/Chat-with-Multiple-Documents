# File: main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from llama_index.core import StorageContext, load_index_from_storage, VectorStoreIndex, SimpleDirectoryReader, ChatPromptTemplate
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import os
from dotenv import load_dotenv
import shutil
import uvicorn
import streamlit as st
import requests
import base64
import docx2txt
import threading

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure the Llama index settings
Settings.llm = HuggingFaceInferenceAPI(
    model_name="meta-llama/Meta-Llama-3-8B-Instruct",
    tokenizer_name="meta-llama/Meta-Llama-3-8B-Instruct",
    context_window=3900,
    token=os.getenv("HF_TOKEN"),
    max_new_tokens=1000,
    generate_kwargs={"temperature": 0.5},
)
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

# Define the directory for persistent storage and data
PERSIST_DIR = "./db"
DATA_DIR = "data"

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PERSIST_DIR, exist_ok=True)

class Query(BaseModel):
    question: str

def data_ingestion():
    documents = SimpleDirectoryReader(DATA_DIR).load_data()
    storage_context = StorageContext.from_defaults()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)

def handle_query(query):
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    chat_text_qa_msgs = [
        (
            "user",
            """You are Q&A assistant named CHAT-DOC. Your main goal is to provide answers as accurately as possible, based on the instructions and context you have been given. If a question does not match the provided context or is outside the scope of the document, kindly advise the user to ask questions within the context of the document.
            Context:
            {context_str}
            Question:
            {query_str}
            """
        )
    ]
    text_qa_template = ChatPromptTemplate.from_messages(chat_text_qa_msgs)
    query_engine = index.as_query_engine(text_qa_template=text_qa_template)
    answer = query_engine.query(query)
    
    if hasattr(answer, 'response'):
        return answer.response
    elif isinstance(answer, dict) and 'response' in answer:
        return answer['response']
    else:
        return "Sorry, I couldn't find an answer."

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".pdf", ".docx", ".txt"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, and TXT are allowed.")
    
    file_path = os.path.join(DATA_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    data_ingestion()
    return {"message": "File uploaded and processed successfully"}

@app.post("/query")
async def query_document(query: Query):
    if not os.listdir(DATA_DIR):
        raise HTTPException(status_code=400, detail="No document has been uploaded yet.")
    
    response = handle_query(query.question)
    return {"response": response}

# Streamlit UI
def streamlit_ui():
    st.title("Chat with your Document 📄")
    st.markdown("Chat here👇")

    icons = {"assistant": "🤖", "user": "👤"}

    if 'messages' not in st.session_state:
        st.session_state.messages = [{'role': 'assistant', "content": 'Hello! Upload a PDF, DOCX, or TXT file and ask me anything about its content.'}]

    for message in st.session_state.messages:
        with st.chat_message(message['role'], avatar=icons[message['role']]):
            st.write(message['content'])

    with st.sidebar:
        st.title("Menu:")
        uploaded_file = st.file_uploader("Upload your document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if st.button("Submit & Process") and uploaded_file:
            with st.spinner("Processing..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                response = requests.post("http://localhost:8000/upload", files=files)
                if response.status_code == 200:
                    st.success("File uploaded and processed successfully")
                else:
                    st.error("Error uploading file")

    user_prompt = st.chat_input("Ask me anything about the content of the document:")

    if user_prompt:
        st.session_state.messages.append({'role': 'user', "content": user_prompt})
        with st.chat_message("user", avatar=icons["user"]):
            st.write(user_prompt)

        # Trigger assistant's response retrieval and update UI
        with st.spinner("Thinking..."):
            response = requests.post("http://localhost:8000/query", json={"question": user_prompt})
            if response.status_code == 200:
                assistant_response = response.json()["response"]
                with st.chat_message("assistant", avatar=icons["assistant"]):
                    st.write(assistant_response)
                st.session_state.messages.append({'role': 'assistant', "content": assistant_response})
            else:
                st.error("Error querying document")

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.start()

    # Run Streamlit (this will run in the main thread)
    streamlit_ui()