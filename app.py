import streamlit as st
from utils import get_response, process_image_api

# Initialize session state for Streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hey there! ✨ Welcome to Niro Ceramic Group—your go-to place for all things tiles, mosaics, and more! Drop your question, and let’s explore together!"
    }]

# Sidebar for file upload (allowing multiple files)
st.sidebar.header("Menu:")
st.sidebar.write("Upload your PDF or Image(s) and click on the 'Submit & Process' button.")
uploaded_files = st.sidebar.file_uploader(
    "Drag and drop files here", 
    type=["pdf", "png", "jpg", "jpeg"], 
    help="Limit 200MB per file",
    accept_multiple_files=True
)

# Add a 'Submit & Process' button in the sidebar
if st.sidebar.button("Submit & Process"):
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                st.sidebar.success(f"PDF file '{uploaded_file.name}' uploaded successfully!")
                # TODO: Process PDF if needed
            else:
                st.sidebar.success(f"Image file '{uploaded_file.name}' uploaded successfully!")
                # Convert the uploaded image file to bytes
                image_bytes = uploaded_file.read()
                # st.write(f"[DEBUG] Uploaded '{uploaded_file.name}' image bytes length:", len(image_bytes))
                response_data = process_image_api(image_bytes)
                # st.write(f"[DEBUG] API response received for '{uploaded_file.name}':", response_data)
                # Check if API response is a list; if so, take first element
                if isinstance(response_data, list):
                    response_data = response_data[0]
                    # st.write("[DEBUG] Converted response_data from list to dict.")
                if "error" not in response_data:
                    data = response_data.get("data", {})
                    exact_match = data.get("direct", [])
                    suggestions = data.get("suggestions", [])
                    exact_info = exact_match[0] if exact_match else {}
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Here is the uploaded image '{uploaded_file.name}' and our tile suggestions below!",
                        "image": image_bytes,
                        "exact_match": exact_info,
                        "suggestions": suggestions
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error processing image '{uploaded_file.name}': {response_data.get('error', 'Unknown error')}"
                    })
    else:
        st.sidebar.warning("No file uploaded!")

# Chat input field
user_input = st.chat_input("Ask anything about Niro Ceramic Group...! 🏺✨")
st.header("Niro Ceramic Group ✨")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = get_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Display the chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # CASE 1: Message with an image and tile suggestions
        if "image" in message and ("exact_match" in message or "suggestions" in message):
            st.write(message["content"])
            st.markdown("**User Uploaded Image:**")
            st.image(message["image"], use_container_width=True)
            
            # Display Exact Match tile info with image
            exact_info = message.get("exact_match", {})
            if exact_info:
                st.markdown("### Exact Match")
                tile_name = exact_info.get("Tile_Name", "Unknown Tile")
                tile_size = exact_info.get("Size", "Unknown Size")
                tile_type = exact_info.get("Type", "Unknown Type")
                item_code = exact_info.get("Item_Code", "Unknown Code")
                avail_qty = exact_info.get("Avail Qty") or exact_info.get("Avail_Qty", "NA")
                item_desc = exact_info.get("Item Desc1", "No Description")
                lotnum = exact_info.get("LotNum", "Unknown Lot")
                wh_loc = exact_info.get("WH loc", "Unknown Location")
                product_url = exact_info.get("Product_URL")
                if product_url:
                    if product_url.startswith("http"):
                        rendered_url = product_url
                    else:
                        if not product_url.startswith("data:"):
                            rendered_url = f"data:image/jpeg;base64,{product_url}"
                        else:
                            rendered_url = product_url
                    col1, col2 = st.columns([1,2])
                    with col1:
                        st.image(rendered_url, use_container_width=True)
                    with col2:
                        st.markdown(f"**Tile Name:** {tile_name}")
                        st.write(f"**Size:** {tile_size}")
                        st.write(f"**Type:** {tile_type}")
                        st.write(f"**Item Code:** {item_code}")
                        st.write(f"**Available Qty:** {avail_qty}")
                        st.write(f"**Item Desc1:** {item_desc}")
                        st.write(f"**LotNum:** {lotnum}")
                        st.write(f"**WH loc:** {wh_loc}")
                else:
                    st.markdown(f"**Tile Name:** {tile_name}")
                    st.write(f"**Size:** {tile_size}")
                    st.write(f"**Type:** {tile_type}")
                    st.write(f"**Item Code:** {item_code}")
                    st.write(f"**Available Qty:** {avail_qty}")
                    st.write(f"**Item Desc1:** {item_desc}")
                    st.write(f"**LotNum:** {lotnum}")
                    st.write(f"**WH loc:** {wh_loc}")
            
            # Display Other Suggestions tile info with images
            suggestions = message.get("suggestions", [])
            if suggestions:
                st.markdown("### Other Suggestions")
                for idx, suggestion in enumerate(suggestions, start=1):
                    st.markdown(f"**Suggestion #{idx}**")
                    s_tile_name = suggestion.get("Tile_Name", "Unknown Tile")
                    s_tile_size = suggestion.get("Size", "Unknown Size")
                    s_tile_type = suggestion.get("Type", "Unknown Type")
                    s_item_code = suggestion.get("Item_Code", "Unknown Code")
                    s_avail_qty = suggestion.get("Avail Qty") or suggestion.get("Avail_Qty", "NA")
                    s_item_desc = suggestion.get("Item Desc1", "No Description")
                    s_lotnum = suggestion.get("LotNum", "Unknown Lot")
                    s_wh_loc = suggestion.get("WH loc", "Unknown Location")
                    # Check for image data in Product_URL or Base64
                    s_product_url = suggestion.get("Product_URL") or suggestion.get("Base64")
                    if s_product_url:
                        if s_product_url.startswith("http"):
                            rendered_s_url = s_product_url
                        else:
                            if not s_product_url.startswith("data:"):
                                rendered_s_url = f"data:image/jpeg;base64,{s_product_url}"
                            else:
                                rendered_s_url = s_product_url
                        col1, col2 = st.columns([1,2])
                        with col1:
                            st.image(rendered_s_url, use_container_width=True)
                        with col2:
                            st.markdown(f"**Tile Name:** {s_tile_name}")
                            st.write(f"**Size:** {s_tile_size}")
                            st.write(f"**Type:** {s_tile_type}")
                            st.write(f"**Item Code:** {s_item_code}")
                            st.write(f"**Available Qty:** {s_avail_qty}")
                            st.write(f"**Item Desc1:** {s_item_desc}")
                            st.write(f"**LotNum:** {s_lotnum}")
                            st.write(f"**WH loc:** {s_wh_loc}")
                    else:
                        st.markdown(f"**Tile Name:** {s_tile_name}")
                        st.write(f"**Size:** {s_tile_size}")
                        st.write(f"**Type:** {s_tile_type}")
                        st.write(f"**Item Code:** {s_item_code}")
                        st.write(f"**Available Qty:** {s_avail_qty}")
                        st.write(f"**Item Desc1:** {s_item_desc}")
                        st.write(f"**LotNum:** {s_lotnum}")
                        st.write(f"**WH loc:** {s_wh_loc}")
                    st.write("---")
        # CASE 2: Message with only an image (no suggestions)
        elif "image" in message:
            st.write(message["content"])
            st.image(message["image"], use_container_width=True)
        # CASE 3: Plain text messages
        else:
            st.write(message["content"])
