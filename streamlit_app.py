import streamlit as st
import requests


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

if __name__ == "__main__":
    streamlit_ui()