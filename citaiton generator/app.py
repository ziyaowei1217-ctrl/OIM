import streamlit as st
import re
import json
import os
from datetime import datetime
import pdfplumber
from dotenv import load_dotenv
from google import genai

# Load env variables from current or parent directory
from dotenv import find_dotenv
env_path = find_dotenv()
load_dotenv(env_path, override=True)

st.set_page_config(
    page_title="SourceMatch | Academic Intel",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium CSS Injection ---
def apply_premium_styling():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Inter:wght@300;400;500&display=swap');

        :root {
            --bg-color: #FFFFFF;
            --sidebar-bg: #F8F9FA;
            --accent-blue: #1A73E8;
            --accent-secondary: #5F6368;
            --card-bg: #FFFFFF;
            --text-main: #202124;
            --text-secondary: #5F6368;
            --border-color: #DADCE0;
            --shadow: 0 1px 3px rgba(60,64,67,0.3), 0 4px 8px rgba(60,64,67,0.15);
        }

        .main {
            background-color: var(--bg-color);
            font-family: 'Inter', sans-serif;
            color: var(--text-main);
        }

        h1, h2, h3 {
            font-family: 'Outfit', sans-serif;
            font-weight: 600;
            color: var(--accent-blue);
            letter-spacing: -0.5px;
        }

        .stButton>button {
            background-color: var(--accent-blue);
            color: white !important;
            font-weight: 500;
            border-radius: 6px;
            border: none;
            transition: all 0.2s ease;
            text-transform: none;
            letter-spacing: normal;
            padding: 0.5rem 1.5rem;
            margin-top: 1rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }

        .stButton>button:hover {
            background-color: #1765CC;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transform: translateY(-1px);
        }

        /* Quote Cards */
        .quote-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 2px 0 rgba(60,64,67,.3), 0 1px 3px 1px rgba(60,64,67,.15);
            transition: box-shadow 0.3s ease;
        }

        .quote-card:hover {
            box-shadow: 0 1px 3px 0 rgba(60,64,67,.3), 0 4px 8px 3px rgba(60,64,67,.15);
        }

        .quote-text {
            font-style: normal;
            font-weight: 400;
            font-size: 1.1rem;
            color: var(--text-main);
            margin-bottom: 16px;
            line-height: 1.6;
            border-left: 4px solid var(--accent-blue);
            padding-left: 15px;
        }

        .quote-meta {
            font-size: 0.85rem;
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            text-transform: none;
            letter-spacing: normal;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--border-color);
        }

        /* Status indicators */
        .stStatus {
            border-radius: 8px;
            background: #F1F3F4;
            border: 1px solid var(--border-color);
        }

        /* Input fields focus */
        .stTextArea textarea:focus {
            border-color: var(--accent-blue) !important;
            box-shadow: 0 0 0 1px var(--accent-blue);
        }

        /* Hide Streamlit components for cleaner look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_premium_styling()

# --- Helper Formatting Functions ---
def to_title_case(s: str) -> str:
    if not s: return ""
    if s.startswith('['): return s
    s = s.lower()
    return re.sub(r'(?:^|\s|-)\S', lambda m: m.group(0).upper(), s)

def to_mla_title_case(s: str) -> str:
    if not s: return ""
    if s.startswith('['): return s
    lowers = {'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'from', 'by', 'of', 'in', 'with'}
    parts = re.split(r'(\s+|-)', s)
    res = []
    for i, word in enumerate(parts):
        if re.match(r'^\s+|-$', word):
            res.append(word)
            continue
        lower_word = word.lower()
        if i == 0 or i == len(parts) - 1 or lower_word not in lowers:
            res.append(lower_word.capitalize())
        else:
            res.append(lower_word)
    return "".join(res)

def to_apa_sentence_case(s: str) -> str:
    if not s: return ""
    if s.startswith('['): return s
    s = s.lower()
    return s.capitalize()

def parse_authors(author_str: str):
    if not author_str or author_str in ('Unknown', 'Unknown Author') or '[Author Name]' in author_str:
        return [{'first': '[Firstname]', 'last': '[Surname]'}]
    
    parts = re.split(r'\s+and\s+|\s*&\s*|;', author_str, flags=re.IGNORECASE)
    parts = [p.strip() for pt in parts for p in pt.split(',')]
    parts = [p for p in parts if p]
    
    if ',' in author_str and 'and' not in author_str.lower() and '&' not in author_str:
        s_parts = author_str.split(',')
        if len(s_parts) == 2:
            return [{'last': to_title_case(s_parts[0].strip()), 'first': to_title_case(s_parts[1].strip())}]
            
    authors = []
    for part in parts:
        names = part.split()
        if len(names) == 1:
            authors.append({'first': '', 'last': to_title_case(names[0])})
        else:
            last = names.pop()
            first = " ".join(names)
            authors.append({'first': to_title_case(first), 'last': to_title_case(last)})
    
    if not authors: return [{'first': '[Firstname]', 'last': '[Surname]'}]
    return authors

def get_in_text_citation(fmt: str, authors: list, year: str, pages: str):
    author_part = ""
    if len(authors) == 1:
        author_part = authors[0]['last']
    elif len(authors) == 2:
        if fmt == 'APA': author_part = f"{authors[0]['last']} & {authors[1]['last']}"
        else: author_part = f"{authors[0]['last']} and {authors[1]['last']}"
    else:
        author_part = f"{authors[0]['last']} et al."

    page_raw = str(pages).strip()
    if page_raw in ('n.p.', 'N/A', ''): page_raw = ""
    
    has_multi = '-' in page_raw or ',' in page_raw or '–' in page_raw
    page_text = re.sub(r'\s*-\s*', '–', page_raw)

    page_part = ""
    if page_text:
        if fmt == 'APA':
            page_part = f"pp. {page_text}" if has_multi else f"p. {page_text}"
        else:
            page_part = page_text

    if fmt == 'APA':
        if page_part: return f"({author_part}, {year}, {page_part})"
        return f"({author_part}, {year})"
    elif fmt == 'MLA':
        if page_part: return f"({author_part} {page_part})"
        return f"({author_part})"
    else: # Chicago
        if page_part: return f"({author_part} {year}, {page_part})"
        return f"({author_part} {year})"

def get_reference_entry(fmt: str, authors: list, year: str, source: str, publisher: str):
    ref_author = ""
    if fmt == 'APA':
        formatted = []
        for a in authors:
            f_name = a['first']
            init = f_name if f_name.startswith('[') else f"{f_name[0]}." if f_name else ""
            res = f"{a['last']}, {init}".strip().rstrip(',')
            formatted.append(res)
        
        if len(formatted) == 1: ref_author = formatted[0]
        elif len(formatted) == 2: ref_author = f"{formatted[0]} & {formatted[1]}"
        else: ref_author = ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
    else:
        if len(authors) == 1:
            ref_author = f"{authors[0]['last']}, {authors[0]['first']}".rstrip(',')
        elif len(authors) == 2:
            ref_author = f"{authors[0]['last']}, {authors[0]['first']}, and {authors[1]['first']} {authors[1]['last']}"
        else:
            ref_author = f"{authors[0]['last']}, {authors[0]['first']}, et al."

    title_case_source = to_mla_title_case(source)
    sentence_case_source = to_apa_sentence_case(source)

    if fmt == 'APA':
        ans = f"{ref_author} ({year}). *{sentence_case_source}*. {publisher}."
    elif fmt == 'MLA':
        ans = f"{ref_author}. *{title_case_source}*. {publisher}, {year}."
    else: # Chicago
        ans = f"{ref_author}. {year}. *{title_case_source}*. [Place of publication]: {publisher}."
    
    return ans.replace('..', '.').replace('..*', '.*')


# --- Initialization ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error(f"GEMINI_API_KEY is not set! Checked for .env at: {env_path}")
    st.stop()

client = genai.Client(api_key=api_key)

if 'outline' not in st.session_state:
    st.session_state.outline = ""
if 'matched_quotes' not in st.session_state:
    st.session_state.matched_quotes = []
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = "Ideation"

# --- Sidebar Navigation ---
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/documents.png", width=80) 
    st.title("SourceMatch")
    st.markdown("---")
    
    # Navigation mapping
    stages = {
        "Ideation": "🖋️ Research Ideation",
        "Evidence": "📚 Source Analysis",
        "Synthesis": "📑 Citation Synthesis"
    }
    
    # Determine progress
    progress_val = 0
    if st.session_state.outline: progress_val = 33
    if st.session_state.matched_quotes: progress_val = 66
    if progress_val == 66 and st.session_state.current_stage == "Synthesis": progress_val = 100
    
    st.write(f"Workflow Progress: {progress_val}%")
    st.progress(progress_val/100)
    
    st.markdown("### Navigation")
    selection = st.radio("Go to", list(stages.values()), index=list(stages.keys()).index(st.session_state.current_stage))
    
    # Sync radio selection back to session state
    st.session_state.current_stage = [k for k, v in stages.items() if v == selection][0]
    
    st.markdown("---")
    st.caption("v.2.0 | Vanguard Edition")

# --- Main Logic ---

if st.session_state.current_stage == "Ideation":
    st.header("🖋️ Step 1: Research Ideation")
    st.info("Define your research focus and let Gemini construct a structural backbone for your paper.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        topic = st.text_area("What is your research focus?", 
                             placeholder="e.g., The socio-economic impact of universal basic income in Nordic countries...",
                             height=150)
        
        if st.button("Generate Paper Outline"):
            if not topic:
                st.warning("Please provide a research focus first.")
            else:
                with st.status("Constructing structural outline...", expanded=True) as status:
                    st.write("Analyzing topic semantics...")
                    prompt = f"You are a professional academic writing assistant.\nCreate a structured outline for a paper based on: {topic}\nReturn JSON with keys 'title' and 'outline'."
                    try:
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt,
                            config={'response_mime_type': 'application/json'}
                        )
                        data = json.loads(res.text)
                        st.session_state.outline = data.get('outline', '')
                        st.write("Outline synthesized. Ready for review.")
                        status.update(label="Outline Generated!", state="complete", expanded=False)
                        st.toast("Success! Outline is ready.")
                    except Exception as e:
                        status.update(label="Generation Failed", state="error")
                        st.error(f"Error: {str(e)}")

    with col2:
        if st.session_state.outline:
            st.markdown("### Structural Result")
            with st.container(border=True):
                st.text(st.session_state.outline)
            st.success("Proceed to 'Source Analysis' in the sidebar once satisfied.")
        else:
            st.markdown("### Structural Result")
            st.empty()

elif st.session_state.current_stage == "Evidence":
    st.header("📚 Step 2: Source Analysis")
    st.info("Upload your source materials (PDFs). We'll extract and align the strongest evidence with your outline.")
    
    if not st.session_state.outline:
        st.warning("⚠️ No outline detected. Please complete the Ideation stage first.")
        st.stop()
        
    uploaded_files = st.file_uploader("Upload scholarly documents (PDF)", accept_multiple_files=True, type=['pdf'])
    
    if st.button("Analyze & Match Evidence") and uploaded_files:
        with st.status("Processing documents...", expanded=True) as status:
            docs = []
            for f in uploaded_files:
                st.write(f"Parsing {f.name}...")
                with pdfplumber.open(f) as pdf:
                    text = ""
                    for page in pdf.pages[:15]: 
                        text += page.extract_text() or ""
                    
                    meta = pdf.metadata or {}
                    author = meta.get('Author', 'Unknown')
                    title = meta.get('Title', 'Unknown')
                    docs.append({
                        "filename": f.name,
                        "author": author,
                        "title": title,
                        "content": text
                    })
            
            st.write("Extracting and mapping quotes with Gemini...")
            sources_str = "\n".join([f"--- Source: {doc['filename']} ---\nMetadata Author: {doc['author']}\nMetadata Title: {doc['title']}\n\n{doc['content']}\n" for doc in docs])
            
            prompt = f"""
            You are a research assistant. Below is an Outline for a paper and text from source documents.
            Extract relevant quotes mapping to each section.

            Outline:
            {st.session_state.outline}

            Sources:
            {sources_str}

            Return EXACTLY a JSON array formatting:
            [
              {{
                "id": "section_identifier",
                "label": "Section Title",
                "quotes": [
                  {{
                    "text": "The exact quote text from the source",
                    "source": "Formal academic title of the document (extract from the text, DO NOT just use the raw filename)",
                    "author": "The author's full name (extract from the document text, usually on the first pages)",
                    "year": "Publication year (extract from the text if available, otherwise 'Unknown')",
                    "publisher": "Publisher or Journal name (extract from the text if available, otherwise 'Unknown')",
                    "page": "Approximate page number or 'N/A'"
                  }}
                ]
              }}
            ]
            """
            try:
                res = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config={'response_mime_type': 'application/json'}
                )
                st.session_state.matched_quotes = json.loads(res.text)
                status.update(label="Evidence Extracted!", state="complete")
                st.toast("Evidence mapping complete.")
            except Exception as e:
                status.update(label="Extraction Failed", state="error")
                st.error(f"Error: {e}")

    if st.session_state.matched_quotes:
        st.markdown("### Matched Evidence Preview")
        for section in st.session_state.matched_quotes[:2]: # Show a snippet
            st.caption(f"Section: {section.get('label')}")
            for q in section.get('quotes', [])[:1]:
                st.markdown(f"> {q.get('text')}")
        st.success("Evidence aligned. Proceed to 'Citation Synthesis' for the final export.")

elif st.session_state.current_stage == "Synthesis":
    st.header("📑 Step 3: Citation Synthesis")
    st.info("Finalize your citations and export the formatted bibliographic data.")
    
    if not st.session_state.matched_quotes:
        st.warning("⚠️ No evidence found. Please complete the Source Analysis stage first.")
        st.stop()
        
    c1, c2 = st.columns([1, 2])
    
    with c1:
        fmt = st.selectbox("Bibliographic Style", ["APA", "MLA", "Chicago"])
        st.markdown("---")
        st.write("#### Reviewing Citations")
        
    export_text = f"{fmt} FORMAT EXPORT\n\n====================\nIN-TEXT CITATIONS\n====================\n\n"
    references = set()
    
    with c2:
        for section in st.session_state.matched_quotes:
            st.subheader(section.get('label', 'Section'))
            export_text += f"{section.get('label', '')}\n\n"
            
            for quote in section.get('quotes', []):
                q_text = quote.get('text', '')
                author_str = quote.get('author') if quote.get('author') not in (None, "", "Unknown", "Unknown Author") else '[Author Name]'
                year = quote.get('year') if quote.get('year') not in (None, "", "Unknown") else str(datetime.now().year)
                page = quote.get('page', 'n.p.')
                source = quote.get('source', 'Unknown Source')
                publisher = quote.get('publisher') if quote.get('publisher') not in (None, "", "Unknown") else '[Publisher]'
                
                parsed_authors = parse_authors(author_str)
                citation_tag = get_in_text_citation(fmt, parsed_authors, year, page)
                
                clean_text = re.sub(r'[.,]$', '', q_text.strip())
                citation = f'"{clean_text}" {citation_tag}.'
                
                ref_str = get_reference_entry(fmt, parsed_authors, year, source, publisher)
                references.add(ref_str)
                
                export_text += f"{citation}\n\n"
                
                # Render Premium Card
                st.markdown(f"""
                    <div class="quote-card">
                        <div class="quote-text">"{clean_text}"</div>
                        <div class="quote-meta">{citation_tag} &nbsp; | &nbsp; {source}</div>
                    </div>
                """, unsafe_allow_html=True)
                
            export_text += "---\n\n"

        export_text += "====================\n"
        export_text += "WORKS CITED\n" if fmt == 'MLA' else ("REFERENCES\n" if fmt == 'APA' else "BIBLIOGRAPHY\n")
        export_text += "====================\n\n"
        
        for ref in sorted(list(references)):
            export_text += f"{ref}\n\n"
            
        st.markdown("### 📤 Final Export")
        st.code(export_text, language='markdown')
        st.download_button("Download Research Kit (.txt)", export_text, file_name="SourceMatch_Export.txt")