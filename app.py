import streamlit as st
import ollama
import requests
import os
from indexer import get_smart_folders, build_index

# 1. Page Config
st.set_page_config(page_title="Visual Memory", page_icon="💾", layout="wide")

# 2. CUSTOM PIXEL ART CSS
css = """

"""
st.markdown(css, unsafe_allow_html=True)

# 3. SIDEBAR: Control Panel
# 3. SIDEBAR: Control Panel
with st.sidebar:
    st.image("https://cataas.com/cat/gif", width=80) 
    st.markdown("## ⚙️ SYS_ADMIN")
    st.markdown("---")
    st.markdown("### DATABASE CONFIG")
    st.write("Index standard folders (Pictures, Desktop, etc.) or specify a custom drive.")
    
    custom_path = st.text_input("Custom Path:", placeholder="D:\\Photos")
    
    if st.button("RUN INDEXER.BAT"):
        with st.spinner("SCANNING SECTORS... Please wait..."):
            try:
                folders = get_smart_folders()
                if custom_path and os.path.exists(custom_path):
                    folders.append(custom_path)
                elif custom_path and not os.path.exists(custom_path):
                    st.warning("Path not found. Indexing default folders only.")
                
                # 1. Run the indexer to save new data to disk
                count = build_index(folders)
                
                # 2. Automatically tell the backend API to reload the data!
                try:
                    requests.post("http://127.0.0.1:8000/reload", timeout=5)
                    st.success(f"✅ INDEX UPDATED AND LOADED. {count} items stored.")
                except requests.exceptions.RequestException:
                    st.warning(f"✅ INDEXED {count} items, but could not reach API to reload. Is main.py running?")
                    
            except Exception as e:
                st.error(f"SYSTEM ERROR: {e}")
# 4. MAIN CHAT INTERFACE
col1, col2 = st.columns([1, 8])
with col1:
    st.image("https://cataas.com/cat/gif", width=60) 
with col2:
    st.title("VISUAL_MEMORY.exe")

def search_local_images(search_term: str) -> str:
    try:
        response = requests.post(
            "http://127.0.0.1:8000/search",
            json={"text": search_term, "top_k": 2}
        )
        data = response.json()
        if not data.get("results"):
            return "No images found."
        
        return " | ".join([f"Found {r['file_path']}" for r in data["results"]])
    except Exception as e:
        return f"Error connecting to API (Is it running?): {e}"

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "system", 
        "content": "You are a helpful offline AI assistant. Use the search_local_images tool to find photos when asked. Reply concisely."
    }]

for msg in st.session_state.messages:
    if msg["role"] not in ["system", "tool"]:
        avatar = ">_" if msg["role"] == "user" else "💾"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if "images" in msg and msg["images"]:
                for img_path in msg["images"]:
                    try:
                        st.image(img_path, caption=img_path, use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not load image at {img_path}")

if prompt := st.chat_input("C:\\Users\\Query> _"):
    with st.chat_message("user", avatar=">_"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="💾"):
        message_placeholder = st.empty()
        
        response = ollama.chat(
            model='llama3.1',
            messages=st.session_state.messages,
            tools=[search_local_images]
        )
        
        if response.message.tool_calls:
            for tool in response.message.tool_calls:
                if tool.function.name == 'search_local_images':
                    term = tool.function.arguments.get('search_term')
                    
                    with st.spinner(f"EXECUTING search_local_images('{term}')..."):
                        tool_result = search_local_images(term)
                        found_paths = [p.replace("Found ", "") for p in tool_result.split(" | ") if "Found " in p]
                        
                        st.session_state.messages.append(response.message)
                        st.session_state.messages.append({"role": "tool", "content": tool_result})
                        
                        final_response = ollama.chat(model='llama3.1', messages=st.session_state.messages)
                        message_placeholder.markdown(final_response.message.content)
                        
                        for img in found_paths:
                            try:
                                st.image(img, caption=img, use_container_width=True)
                            except:
                                pass
                                
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": final_response.message.content,
                            "images": found_paths
                        })
        else:
            message_placeholder.markdown(response.message.content)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response.message.content
            })