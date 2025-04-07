import os
import re
import smtplib
from dotenv import load_dotenv
import langid
from groq import Groq
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

# Restrict langid to detect only English
langid.set_languages(["en"])

# Initialize chat history and global variables
MAX_HISTORY = 5
chat_history = []

# Store extracted values
current_tile_name = "Unknown Tile"
current_required_qty = "0"
current_tile_size = "15x20"  # Default size

# Email credentials
SENDER_EMAIL = "srimathi.j@kgisl.com"
SENDER_PASSWORD = "Srima()123"  # Use an App Password
RECEIVER_EMAIL = "srimathi.j@kgisl.com"  # Receiver email

def detect_language(text):
    """Detects language using langid."""
    try:
        detected_lang, _ = langid.classify(text)
        print(f"[DEBUG] Detected language: {detected_lang}")
        return detected_lang
    except Exception as e:
        print(f"[DEBUG] Error detecting language: {e}")
        return "en"

def trim_chat_history():
    """Limits chat history to the last MAX_HISTORY exchanges."""
    global chat_history
    chat_history = chat_history[-MAX_HISTORY:]
    print(f"[DEBUG] Chat history trimmed. Length now: {len(chat_history)}")

def extract_tile_name(question):
    """
    Extracts the tile name from user input.
    Example: "I want to order GDW04 Legna Castano tile" -> "GDW04 Legna Castano"
    """
    match = re.search(r'order (.+?)(?: tile|$)', question, re.IGNORECASE)
    tile_name = match.group(1).strip() if match else "Unknown Tile"
    print(f"[DEBUG] Extracted tile name: {tile_name}")
    return tile_name

def extract_tile_size(question):
    """
    Extracts the tile size (e.g., 15x20) from user input.
    """
    match = re.search(r'(\d+x\d+)', question, re.IGNORECASE)
    tile_size = match.group(1) if match else None
    print(f"[DEBUG] Extracted tile size: {tile_size}")
    return tile_size

def extract_required_qty(question):
    """
    Extracts the required quantity from user input.
    """
    match = re.search(r'(\d+)\s*(?:units|tiles|pieces)?', question, re.IGNORECASE)
    required_qty = match.group(1) if match else None
    print(f"[DEBUG] Extracted required quantity: {required_qty}")
    return required_qty

def send_order_confirmation_email(tile_name, required_qty, tile_size):
    """
    Sends an order confirmation email with tile details.
    """
    subject = "Tile Order Confirmation"
    html = f"""\
    <html>
        <head></head>
        <body>
            <h4>Hi Srimathi,</h4>
            <p>
                We are pleased to confirm your order for <strong>{required_qty}</strong> tiles of <strong>{tile_name}</strong> 
                with the following specifications:
            </p>
            <ul>
                <li><strong>Size:</strong> {tile_size}</li>
            </ul>
            <p>
                Thank you for choosing Niro Granite!
            </p>
            <br>
            <p>Best regards,</p>
            <p>Niro Ceramics</p>
        </body>
    </html>
    """
    message = MIMEMultipart()
    message['From'] = SENDER_EMAIL
    message['To'] = RECEIVER_EMAIL
    message['Subject'] = subject
    message.attach(MIMEText(html, 'html'))
    
    docx_filename = "Tiles_Proposal.docx"
    if os.path.exists(docx_filename):
        try:
            with open(docx_filename, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{docx_filename}"')
            message.attach(part)
            print(f"[DEBUG] Attached file: {docx_filename}")
        except Exception as e:
            print(f"[DEBUG] Error reading attachment file: {e}")
    else:
        print(f"[DEBUG] File not found: {docx_filename}")

    try:
        print("[DEBUG] Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        print("[DEBUG] Logging in to SMTP server...")
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print(f"[DEBUG] Sending order confirmation to {RECEIVER_EMAIL}...")
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())
        server.quit()
        print("[DEBUG] Order confirmation email sent successfully.")
        return (
            "Thank you for your confirmation. Your order has been processed. "
            "You should receive an email with the order details shortly."
        )
    except Exception as e:
        print(f"[DEBUG] SMTP Error: {e}")
        return f"Failed to send confirmation email: {e}"

def get_response(question):
    """
    Handles user interactions and triggers email sending when needed.
    Extracts tile_name, required_qty, and tile_size from the latest user message.
    """
    global chat_history, current_tile_name, current_required_qty, current_tile_size

    if not question.strip():
        return "Please provide a valid question."

    try:
        lang = detect_language(question)
        extracted_name = extract_tile_name(question)
        extracted_size = extract_tile_size(question)
        extracted_qty = extract_required_qty(question)

        if extracted_name != "Unknown Tile":
            current_tile_name = extracted_name
        if extracted_size:
            current_tile_size = extracted_size
        if extracted_qty:
            current_required_qty = extracted_qty
        if current_required_qty == "0":
            current_required_qty = "6"  # fallback

        urls = """
        **Relevant Source:**
        - [Niro Ceramic Group](https://niroceramic.com/)
        """
        chat_history.append({"role": "user", "content": question})
        trim_chat_history()

        confirm_keywords = ["yes", "yeah", "confirm", "proceed", "ok"]
        if question.strip().lower() in confirm_keywords:
            return send_order_confirmation_email(
                current_tile_name,
                current_required_qty,
                current_tile_size
            )

        template_en = f"""You are an AI assistant specializing in **Niro Ceramic Group** products, including **porcelain and ceramic tiles, glass mosaics, and bathroom sanitaryware**. Your primary goal is to assist users efficiently in ordering tiles while providing accurate information about **Niro Ceramic Group** and its website.

        ## **Ordering Flow:**
        ### 1️⃣ **Tile Selection:**  
        - If the user expresses interest in ordering tiles (e.g., *"I would love to order some tiles"*), ask for the tile name.  
        - Once the user provides the tile name, fetch and display the details in a structured table format:  

            | **Tile Name**  | **Size** | **Available Qty** | **Product URL** |
            |----------------|----------|-------------------|-----------------|
            | {current_tile_name} | {current_tile_size}   | 6 | [View Product](https://www.nirogranite.co.id/product/{current_tile_name.replace(' ', '-').lower()}/) |

        - Follow up with:  
            **"Here are the details. How many units would you like to order?"**

        ### 2️⃣ **Quantity Confirmation:**  
        - When the user specifies the quantity (e.g., *"I need 5 units"*), generate an updated order confirmation table:  

            | **Tile Name**  | **Size**  | **Required Qty** | **Product URL** |
            |----------------|-----------|------------------|-----------------|
            | {current_tile_name} | {current_tile_size} | {current_required_qty} | [View Product](https://www.nirogranite.co.id/product/{current_tile_name.replace(' ', '-').lower()}/) |

        - Follow up with:  
            **"Would you like to confirm your order? Alternatively, if you'd like to explore more tile options, you can upload an image for matching or search by name."**

        ### 3️⃣ **Order Finalization:**  
        - If the user confirms with **"Yes," "Proceed," "Confirm," "Yeah"**, respond with:  
            **"Thank you! Your order for {current_required_qty} units of {current_tile_name} (size {current_tile_size}) has been placed. A confirmation email has been sent to your registered email address."**

        ## **General Niro Ceramic Group Information:**
        - If the user asks about **company details, headquarters, store locations, or website-related queries**, provide accurate information.  
        - If the user asks about **website navigation, customer support, or product catalogs**, provide relevant details or direct them to the appropriate page.

        ## **Exception Handling:**
        - If the user's question or request is outside the scope of Niro Ceramic Group products (for example, unrelated topics or out-of-box questions), respond with:  
        **"I am only trained to assist with inquiries related to Niro Ceramic Group products and their ordering process."**

        ## **Reference Source:**  
        {urls}

        ## **User Input:**  
        {question}

        ## **Chat History:**  
        {chat_history}

        ## **Response:**  
        """
        print(f"[DEBUG] Using prompt: {template_en[:100]}...")
        if not any(msg["role"] == "system" for msg in chat_history):
            chat_history.insert(0, {"role": "system", "content": template_en})

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=chat_history,
            temperature=1,
            max_tokens=500,
            top_p=1,
            stream=False,
            stop=None,
        )
        response = completion.choices[0].message.content.strip()
        chat_history.append({"role": "assistant", "content": response})
        print(f"[DEBUG] Generated response: {response}")
        return response

    except Exception as e:
        print(f"[DEBUG] Error generating response: {e}")
        return "Sorry, I encountered an issue while generating a response. Please try again later."

######################################
# New functions to process image API #
######################################
import requests
import base64
import traceback

def send_to_backend(payload):
    """
    Sends the image data to the backend.
    """
    url = "http://13.200.171.249:5002/medicalbill_api"
    headers = {
        'Authorization': 'a51110f2d8ba765d54184aecfb9b86dca033f676b10447cf131239c1c7af11cthaimedicalbill'
    }
    try:
        print(f"[DEBUG] Sending payload to backend. Keys: {list(payload.keys())}")
        response = requests.post(url, data=payload, headers=headers)
        print(f"[DEBUG] Backend response status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            print(f"[DEBUG] Backend response data: {response_data}")
            return response_data
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"[DEBUG] Error sending request: {e}")
        return {"error": str(e)}

def process_image_api(image_bytes):
    """
    Encodes the image in Base64 and sends it to the backend API.
    """
    try:
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        payload = {
            "selectedBcaseId": "1",
            "loginUserId": "2",
            "api_data": "API",
            "decode_key": "Encode",
            "file": f"data:image/jpeg;base64,{base64_image}"
        }
        print("[DEBUG] Process image API payload created.")
        response_data = send_to_backend(payload)
        return response_data
    except Exception as e:
        print(f"[DEBUG] Error in processing image: {e}")
        return {"error": str(e)}

# Example usage for debugging
if __name__ == "__main__":
    while True:
        user_input = input("\nEnter your question (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        response = get_response(user_input)
        print("\nResponse:\n", response)
