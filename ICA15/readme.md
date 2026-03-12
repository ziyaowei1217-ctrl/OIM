\# URL Content Extractor



This is a minimal Streamlit web application designed to fetch and extract content from a given URL. 



\## Features

\- Paste any URL into the input field.

\- Fetches the raw text content of the webpage.

\- Displays the \*\*first 200 characters\*\* of the extracted text.

\- Calculates and displays the \*\*total word count\*\* of the content.

\- Robust error handling using `st.error` for invalid URLs or connection issues.



\## Prerequisites

Ensure you have Python installed. You will need to install the following libraries:



```bash

pip install streamlit requests beautifulsoup4

