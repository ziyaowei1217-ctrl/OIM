#Professor the page always told me "model not found", I have no idea why. Probably something goes wrong with my environment?
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI
import streamlit as st
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
Settings.llm = GoogleGenAI(model='models/gemini-1.5-flash', api_key=api_key)
Settings.embed_model = GoogleGenAIEmbedding(model_name='models/embedding-001', api_key=api_key)

@st.cache_resource
def initialize_index():
    if not os.path.exists("./data"):
        st.error("Please make sure the 'data' directory exists and contains the documents to be indexed.")
        return None
    documents = SimpleDirectoryReader("./data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    return index.as_query_engine()

if "message" not in st.session_state:
    st.session_state.message = []
for message in st.session_state.message:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

query_engine = initialize_index()

prompt = st.chat_input("You got any questions about the manual? Ask me!")
if prompt:
    st.session_state.message.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if query_engine:
            with st.spinner("Checking the manual now!"):
                response = query_engine.query(prompt)
                full_response = str(response)
                st.markdown(full_response)
                st.session_state.message.append({"role": "assistant", "content": full_response})