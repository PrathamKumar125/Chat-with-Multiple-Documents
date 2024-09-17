import streamlit as st
from llama_index.core import StorageContext, load_index_from_storage, VectorStoreIndex, SimpleDirectoryReader, ChatPromptTemplate
from llama_index.llms.huggingface import HuggingFaceInferenceAPI
from dotenv import load_dotenv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
import os
import base64
import docx2txt

# Load environment variables
load_dotenv()

icons = {"assistant": "robot.png", "user": "man-kddi.png"}

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

def displayPDF(file):
    with open(file, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def displayDOCX(file):
    text = docx2txt.process(file)
    st.text_area("Document Content", text, height=400)

def displayTXT(file):
    with open(file, "r") as f:
        text = f.read()
    st.text_area("Document Content", text, height=400)

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

# Streamlit app initialization
st.title("Chat with your Document 📄")
st.markdown("Chat here👇")

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
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            filepath = os.path.join(DATA_DIR, "uploaded_file" + file_extension)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if file_extension == ".pdf":
                displayPDF(filepath)
            elif file_extension == ".docx":
                displayDOCX(filepath)
            elif file_extension == ".txt":
                displayTXT(filepath)
            
            data_ingestion()  # Process file every time a new file is uploaded
            st.success("Done")

user_prompt = st.chat_input("Ask me anything about the content of the document:")

if user_prompt and uploaded_file:
    st.session_state.messages.append({'role': 'user', "content": user_prompt})
    with st.chat_message("user", avatar=icons["user"]):
        st.write(user_prompt)

    # Trigger assistant's response retrieval and update UI
    with st.spinner("Thinking..."):
        response = handle_query(user_prompt)
        with st.chat_message("assistant", avatar=icons["assistant"]):
            st.write(response)
        st.session_state.messages.append({'role': 'assistant', "content": response})
