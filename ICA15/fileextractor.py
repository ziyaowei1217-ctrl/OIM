import streamlit as st
import requests
from bs4 import BeautifulSoup

# 设置页面标题
st.title("🔗 URL Content Extractor")
st.write("Paste a URL below to extract its text content and word count.")

# 1. 接收用户输入的 URL
url = st.text_input("Enter URL:")

if url:
    # 2 & 3. 尝试抓取内容并进行错误处理
    try:
        # 添加 headers 伪装成浏览器，防止被某些网站轻易拦截
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        # 如果状态码不是 200 (成功)，抛出异常
        response.raise_for_status()
        
        # 使用 BeautifulSoup 解析 HTML 并提取纯文本
        soup = BeautifulSoup(response.text, 'html.parser')
        raw_text = soup.get_text(separator=' ', strip=True)
        
        if not raw_text:
            st.warning("Successfully fetched the page, but no text content was found.")
        else:
            # 4. 获取前 200 个字符
            first_200_chars = raw_text[:200]
            
            # 5. 计算总字数 (按空格分割)
            word_count = len(raw_text.split())
            
            # 展示结果
            st.subheader("Results")
            st.write("### First 200 Characters:")
            st.info(first_200_chars + ("..." if len(raw_text) > 200 else ""))
            
            st.write("### Word Count:")
            st.success(f"**{word_count}** words")
            
    # 捕获网络请求相关的错误 (例如：无效网址、连接超时等)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the URL: {e}")
    # 捕获其他未知错误
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")