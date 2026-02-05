# OIM Classwork Repository

A collection of coursework and projects from Operations and Information Management (OIM) classes, focusing on Python programming, data processing, and AI/ML applications using LlamaIndex and various LLM frameworks.

## 👤 About Me

[Your brief bio here - e.g., "I'm a student at Babson College studying Operations and Information Management. I'm passionate about leveraging AI and data analytics to solve business problems"]

## 🛠️ Skills & Tools

### Languages
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=sql&logoColor=white)

### Libraries & Frameworks
![LlamaIndex](https://img.shields.io/badge/LlamaIndex-000000?style=for-the-badge&logo=llama&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![python-dotenv](https://img.shields.io/badge/python--dotenv-000000?style=for-the-badge)

### Tools
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

## 📁 Directory Structure

```
OIM/
│
├── README.md                                    # Project documentation
│
├── In-Class Activity 1/                        # Python fundamentals and Git setup
│   ├── 02-python_concepts.ipynb                # Python programming concepts
│   ├── image-1.png                             # Git configuration proof
│   ├── image.png                               # Repository screenshot
│   └── In-Class Activity 1.word                # Activity documentation
│
└── In-class Activity 2 - Creating a llama index/    # LlamaIndex and LLM projects
    ├── 03-demo_create_llamaindex.py                 # Create LlamaIndex from PDF documents
    ├── 03-demo_llama_retrieval.py                    # Document retrieval with OpenAI
    ├── 03-demo_llama_gemini_retrieval.py            # Document retrieval with Google Gemini
    ├── run_with_env.py                               # Environment setup helper
    └── data/                                         # PDF documents for processing
        ├── Notes1.pdf
        ├── Notes2.pdf
        └── Notes3.pdf
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Clone the Repository

```bash
git clone https://github.com/[your-username]/[your-repo-name].git
cd [your-repo-name]
```

### Install Dependencies

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install required packages:

```bash
pip install llama-cloud-services
pip install llama-index
pip install llama-index-llms-openai
pip install llama-index-llms-gemini
pip install llama-index-llms-huggingface
pip install llama-index-embeddings-huggingface
pip install sentence-transformers
pip install python-dotenv
pip install pandas
pip install scikit-learn
pip install streamlit
```

Or install from requirements.txt (if available):

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory with your API keys:

```env
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
ORGANIZATION_ID=your_organization_id_here
OPENAI_API_KEY=your_openai_api_key_here  # If using OpenAI
```

### Running the Code

**Jupyter Notebooks:**
```bash
# Navigate to the activity folder
cd "In-Class Activity 1"
jupyter notebook 02-python_concepts.ipynb
```

**Python Scripts - LlamaIndex Projects:**
```bash
# Navigate to the LlamaIndex activity folder
cd "In-class Activity 2 - Creating a llama index"

# Run LlamaIndex creation script
python 03-demo_create_llamaindex.py

# Run retrieval with OpenAI
python 03-demo_llama_retrieval.py

# Run retrieval with Gemini
python 03-demo_llama_gemini_retrieval.py
```

**Note:** Make sure your `.env` file is properly configured with the required API keys before running the scripts.

## 📧 Contact & Connect

- **LinkedIn:** [Your LinkedIn Profile URL](https://linkedin.com/in/yourprofile)
- **Personal Website:** [Your website URL](https://yourwebsite.com)
- **Portfolio:** [Your portfolio URL](https://yourportfolio.com)
- **Email:** [your.email@example.com](mailto:your.email@example.com)

---

## 📝 Project Overview

This repository contains hands-on assignments and projects covering:

- **Python Fundamentals:** Variables, data structures, and basic programming concepts
- **Document Processing:** PDF parsing and text extraction using LlamaParse
- **AI/ML Applications:** Building and querying vector indexes with LlamaIndex
- **LLM Integration:** Working with OpenAI, Google Gemini, and HuggingFace models
- **Version Control:** Git and GitHub workflow practices

*This repository contains coursework and projects from Operations and Information Management classes at Babson College.*
