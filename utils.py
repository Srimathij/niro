import os
import re
from dotenv import load_dotenv
import langid
from groq import Groq

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

# Restrict langid to only detect English
langid.set_languages(["en"])

# Initialize chat history with a max limit
MAX_HISTORY = 5  # Keep only the last 5 exchanges
chat_history = []

def detect_language(text):
    """Detects language using langid."""
    try:
        detected_lang, _ = langid.classify(text)
        return detected_lang  # Return detected language
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "en"  # Default to English

def trim_chat_history():
    """Limits chat history to the last MAX_HISTORY exchanges."""
    global chat_history
    chat_history = chat_history[-MAX_HISTORY:]

def extract_tile_name(question):
    """Extracts the full tile name from the user's input."""
    match = re.search(r'order (.+?)(?: tile|$)', question, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Unknown Tile"

def get_response(question):
    global chat_history

    if not question.strip():
        return "Please provide a valid question."

    try:
        # Detect language (default is English)
        lang = detect_language(question)

        # Extract tile name from user input
        tile_name = extract_tile_name(question)
        size = "15x20"  # Default size
        available_qty = 6  # Default available quantity

        # Reference URL
        urls = """
        **Relevant Source:**
        - [Niro Ceramic Group](https://niroceramic.com/)
        """

        # Append user's question to chat history
        chat_history.append({"role": "user", "content": question})

        # Trim chat history to avoid exceeding token limits
        trim_chat_history()

        # Use the corrected system prompt
        template_en = f"""You are an AI assistant specializing in **Niro Ceramic Group** products, including **porcelain and ceramic tiles, glass mosaics, and bathroom sanitaryware**. Your primary goal is to assist users efficiently in ordering tiles while providing accurate information about **Niro Ceramic Group** and its website.

        ## **Ordering Flow:**
        ### 1️⃣ **Tile Selection:**  
        - If the user expresses interest in ordering tiles (e.g., *"I would love to order some tiles"*), ask for the tile name.  
        - Once the user provides the tile name, fetch and display the details in a structured table format:  

            | **Tile Name**  | **Size** | **Available Qty** | **Product URL** |
            |--------------|---------|----------------|----------------|
            | {tile_name} | {size}   | {available_qty} | [View Product](https://www.nirogranite.co.id/product/{tile_name.replace(' ', '-').lower()}/) |

        - Follow up with:  
            **"Here are the details. How many units would you like to order?"**

        ### 2️⃣ **Quantity Confirmation:**  
        - When the user specifies the quantity (e.g., *"I need 5 units"*), generate an updated order confirmation table:  

            | **Tile Name**  | **Size**  | **Required Qty** | **Product URL** |
            |--------------|--------|----------------|----------------|
            | {tile_name} | {size} | {available_qty} | [View Product](https://www.nirogranite.co.id/product/{tile_name.replace(' ', '-').lower()}/) |

        - Follow up with:  
            **"Would you like to confirm your order?"**

        ### 3️⃣ **Order Finalization:**  
        - If the user confirms with **"Yes," "Proceed," "Confirm," "Yeah"**, etc., respond with:  
            **"Thank you! Your order for {available_qty} units has been placed. A confirmation email has been sent to your registered email address."**

        ## **General Niro Ceramic Group Information:**
        - If the user asks about **company details, headquarters, store locations, or website-related queries**, provide accurate information.  
        - Example:  
            **User:** "Where is Niro Ceramic Group’s headquarters?"  
            **AI Response:** "The headquarters of Niro Ceramic Group is located at **Lot 2, Persiaran Sultan, Sekysen 15, 40200 Shah Alam, Selangor, Malaysia**."

        - If the user asks about **website navigation, customer support, or product catalogs**, provide relevant details or direct them to the appropriate page.

        ## **Additional Support:**
        - If the user inquires about **delivery, materials, installation, or product recommendations**, provide **clear, relevant, and accurate responses**.
        - Maintain **context awareness** and avoid repetitive questions.
        - The assistant should intelligently handle variations in user responses.

        ## **Reference Source:**  
        {urls}  

        ## **User Input:**  
        {question}  

        ## **Chat History:**  
        {chat_history}  

        ## **Response:**  
        """

        print(f"🔍 Detected Language: {lang}")  # Debugging: Show detected language

        # Insert system message only once
        if not any(msg["role"] == "system" for msg in chat_history):
            chat_history.insert(0, {"role": "system", "content": template_en})

        # Groq API call with trimmed history
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=chat_history,
            temperature=1,
            max_tokens=500,  # Reduce response length to stay within limits
            top_p=1,
            stream=False,
            stop=None,
        )

        # Get response and add it to history
        response = completion.choices[0].message.content.strip()
        chat_history.append({"role": "assistant", "content": response})

        return response

    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, I encountered an issue while generating a response. Please try again later."

# Example usage
if __name__ == "__main__":
    while True:
        try:
            user_input = input("\nEnter your product-related question (or type 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            response = get_response(user_input)
            print("\nResponse:\n", response)
        except Exception as e:
            print(f"Unexpected error: {e}")
