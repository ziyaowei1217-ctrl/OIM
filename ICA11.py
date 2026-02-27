import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.google_genai import GoogleGenAI

def validate_config():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Cannot find GOOGLE_API_KEY in environment variables.")
        st.info("Please set GOOGLE_API_KEY=Your API Key in your .env file.")
        st.stop()  
    return api_key

@st.cache_resource(show_spinner=False)
def get_query_engine():
    data_path = "./data"

    if not os.path.exists(data_path):
        st.error(f"cannot find the directory '{data_path}'。")
        st.stop()
    if not os.listdir(data_path):
        st.error(f"No documents found in '{data_path}' directory. Please add some files to index.")
        st.stop()
    try:
        with st.spinner("Initializing RAG Engine..."):
            Settings.chunk_size = 512
            Settings.chunk_overlap = 50
            Settings.llm = GoogleGenAI(model="models/gemini-2.5-flash")
            Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

            documents = SimpleDirectoryReader(data_path).load_data()
            index = VectorStoreIndex.from_documents(documents)
            
            return index.as_query_engine(similarity_top_k=5, response_mode="compact")
            
    except Exception as e:
        st.error(f"Failed to initialize RAG Engine: {str(e)}")
        st.stop()

def main():
    st.set_page_config(page_title="Babson Handbook RAG System", layout="centered")
    st.title("Babson Handbook")
    validate_config()
    query_engine = get_query_engine()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("_Ask me anything about the Babson Handbook..._"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            try:
                with st.spinner(""):
                    response = query_engine.query(prompt)
                    bot_response = response.response
                    st.markdown(bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
            except Exception as e:
                st.error(f"Error processing query: {str(e)}")

if __name__ == "__main__":
    main()