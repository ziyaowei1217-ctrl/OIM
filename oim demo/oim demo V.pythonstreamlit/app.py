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

st.set_page_config(page_title="SourceMatch Prototype", layout="wide")

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

def to_sentence_case(s: str) -> str:
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
    sentence_case_source = to_sentence_case(source)

    if fmt == 'APA':
        ans = f"{ref_author} ({year}). *{sentence_case_source}*. {publisher}."
    elif fmt == 'MLA':
        ans = f"{ref_author}. *{title_case_source}*. {publisher}, {year}."
    else: # Chicago
        ans = f"{ref_author}. {year}. *{title_case_source}*. [Place of publication]: {publisher}."
    
    return ans.replace('..', '.').replace('..*', '.*')


# --- App Logic ---
st.title("SourceMatch Prototype (Streamlit Edition)")
st.write("A rapid Python alternative to the React wizard.")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error(f"GEMINI_API_KEY is not set! Checked for .env at: {env_path}")
    st.stop()

client = genai.Client(api_key=api_key)

if 'outline' not in st.session_state:
    st.session_state.outline = ""
if 'matched_quotes' not in st.session_state:
    st.session_state.matched_quotes = []

with st.expander("Step 1: Generate Outline", expanded=not st.session_state.outline):
    topic = st.text_area("Describe your paper topic", height=100)
    if st.button("Generate Outline"):
        with st.spinner("Generating Outline with Gemini..."):
            prompt = f"You are a professional academic writing assistant.\nCreate a structured outline for a paper based on: {topic}\nReturn JSON with keys 'title' and 'outline'."
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            data = json.loads(res.text)
            st.session_state.outline = data.get('outline', '')

if st.session_state.outline:
    st.markdown("### Current Outline")
    st.text(st.session_state.outline)

with st.expander("Step 2 & 3: Upload Sources & Match", expanded=st.session_state.outline != "" and not st.session_state.matched_quotes):
    uploaded_files = st.file_uploader("Upload PDF Documents", accept_multiple_files=True, type=['pdf'])
    
    if st.button("Extract & Match Quotes") and uploaded_files:
        with st.spinner("Parsing PDFs and extracting mapping..."):
            docs = []
            for f in uploaded_files:
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
            res = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            try:
                st.session_state.matched_quotes = json.loads(res.text)
            except Exception as e:
                st.error("Failed to parse JSON response from Gemini")
                st.write(res.text)

if st.session_state.matched_quotes:
    st.markdown("### Step 4: Export Citations")
    
    fmt = st.selectbox("Select Display Format", ["APA", "MLA", "Chicago"])
    
    export_text = f"{fmt} FORMAT EXPORT\n\n====================\nIN-TEXT CITATIONS\n====================\n\n"
    references = set()
    
    for section in st.session_state.matched_quotes:
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
            
            # Show natively in small cards
            with st.container(border=True):
                st.markdown(f"*{clean_text}*")
                st.caption(f"{citation_tag} — {source}")
                
        export_text += "---\n\n"

    export_text += "====================\n"
    export_text += "WORKS CITED\n" if fmt == 'MLA' else ("REFERENCES\n" if fmt == 'APA' else "BIBLIOGRAPHY\n")
    export_text += "====================\n\n"
    
    for ref in sorted(list(references)):
        export_text += f"{ref}\n\n"
        
    st.markdown("##### Final Export Document (Hover top right to Copy)")
    st.code(export_text, language='markdown')
