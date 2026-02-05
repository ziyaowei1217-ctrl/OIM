# pip install llama-cloud-services

"""
Upload and ingest data
requires llama_cloud-services
pip install llama-cloud-services
"""
from dotenv import load_dotenv
from llama_cloud_services import LlamaCloudIndex
from llama_cloud_services import LlamaParse
import os
load_dotenv()
api_key = os.getenv("LLAMA_CLOUD_API_KEY")  
if api_key:
    print("API key loaded successfully")
else:
    print("ERROR: API key not found in .env file")
    exit()  
parser = LlamaParse(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
if api_key:
    print("API key loaded successfully")
else:
    print("ERROR: API key not found in .env file")
job_result = parser.parse( 'data/Notes1.pdf') #can also be a list of documents
documents = job_result.get_text_documents() #returns a list even if only one document
if documents:
    print(f"Successfully parsed beginning with {documents[0].text[:1000]}: ")
else:
    print("no document(s) to parse")
index = LlamaCloudIndex.from_documents(documents, name= "AI_Proposal")

print(index.id)