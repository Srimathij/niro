# app.py

import streamlit as st
from utils import get_response

# Initialize session state for Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey there! ✨ Welcome to Niro Ceramic Group—your go-to place for all things tiles, mosaics, and more! Drop your question, and let’s explore together!"}
    ]

# Chat input field at the top
user_input = st.chat_input("𝑨𝒔𝒌 𝒂𝒏𝒚𝒕𝒉𝒊𝒏𝒈 𝒂𝒃𝒐𝒖𝒕 𝑵𝒊𝒓𝒐 𝑪𝒆𝒓𝒂𝒎𝒊𝒄 𝑮𝒓𝒐𝒖𝒑...! 🏺✨")

# Streamlit title
st.header("ɴɪʀᴏ ᴄᴇʀᴀᴍɪᴄ ɢʀᴏᴜᴘ✨")

# Process user input
if user_input:
    # Add the user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Get RAG + Groq response
    response = get_response(user_input)
    
    # Add the assistant response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display the full chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])