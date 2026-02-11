import streamlit as st
import os
from dotenv import load_dotenv
from llama_cloud_services import LlamaCloudIndex
from llama_index.llms.openai import OpenAI

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="LlamaIndex Query App", layout="wide")
st.title("📚 LlamaIndex Document Query")

# Check for required environment variables
api_key = os.getenv("LLAMA_CLOUD_API_KEY")
org_id = os.getenv("ORGANIZATION_ID")

if not api_key or not org_id:
    st.error("⚠️ Missing environment variables. Please check your .env file.")
    st.info("Required variables: LLAMA_CLOUD_API_KEY and ORGANIZATION_ID")
    st.stop()

# Initialize session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    index_name = st.text_input("Index Name", value="AI_Proposal")
    project_name = st.text_input("Project Name", value="Default")
    st.divider()
    st.info("Configure your LlamaIndex settings above")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Query Your Documents")
    query = st.text_area(
        "Enter your question:",
        height=100,
        placeholder="What would you like to know about the documents?"
    )
    
    if st.button("🚀 Search", use_container_width=True):
        if query.strip():
            with st.spinner("Searching documents..."):
                try:
                    # Initialize the LlamaCloud index
                    index = LlamaCloudIndex(
                        name=index_name,
                        project_name=project_name,
                        api_key=api_key,
                        organization_id=org_id
                    )
                    
                    # Retrieve relevant nodes
                    retriever = index.as_retriever()
                    results = retriever.retrieve(query)
                    
                    # Display results
                    st.success("✅ Query completed!")
                    
                    st.subheader("📋 Top Results")
                    for i, result in enumerate(results[:3], 1):
                        with st.expander(f"Result {i} (Score: {result.score:.2f})"):
                            st.write(result.text)
                    
                    # Add to history
                    st.session_state.query_history.append({
                        "query": query,
                        "results_count": len(results)
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Make sure your LlamaIndex is properly configured and indexed.")
        else:
            st.warning("Please enter a question.")

with col2:
    st.subheader("📊 Query History")
    if st.session_state.query_history:
        for i, item in enumerate(st.session_state.query_history[-5:], 1):
            with st.expander(f"Query {i}"):
                st.write(f"**Question:** {item['query']}")
                st.write(f"**Results:** {item['results_count']}")
    else:
        st.info("No queries yet.")

# Footer
st.divider()
st.caption("Powered by LlamaIndex and Streamlit")
