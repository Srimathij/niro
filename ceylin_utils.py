import os
from dotenv import load_dotenv
import re
import langid
from groq import Groq

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

# Restrict `langid` to only detect English, Tamil, and Sinhala
langid.set_languages(["en", "ta", "si"])

def detect_language(text):
    """Detects language using both langid and Unicode fallback to ensure accuracy."""
    detected_lang, confidence = langid.classify(text)

    # Stronger Sinhala & Tamil Unicode check
    if re.search(r'[\u0D80-\u0DFF]', text):  # Sinhala Unicode range
        return 'si'
    elif re.search(r'[\u0B80-\u0BFF]', text):  # Tamil Unicode range
        return 'ta'

    return detected_lang  # Return langid result if no Unicode match

def get_response(question):
    if not question.strip():
        return "Please provide a valid question."

    # Detect the language of the question
    lang = detect_language(question)

    # Reference URL
    urls = """
    **Relevant Insurance Source:**
    - [Ceylinco Life](https://www.ceylincolife.com/)
    """

    # English Prompt Template
    template_en = f"""You are a specialized insurance assistant designed to provide **accurate**, **reliable**, and **up-to-date** information.

    Your responses should be:
    - **Clear and structured** (point-wise format)
    - **Focused on insurance policies, benefits, and coverage**
    - **Rooted in trusted sources** like Ceylinco Life

    Reference the following source for insights:
    {urls}

    Begin with a warm and engaging introduction before delivering your response professionally and insightfully.

    Question: {question}

    Answer:
    """

    # Tamil Prompt Template
    template_ta = f"""நீங்கள் ஒரு நம்பகமான காப்பீட்டு உதவியாளர். நீங்கள் வழங்கும் தகவல்கள் **துல்லியமானவை**, **நம்பகமானவை**, மற்றும் **சமீபத்தியவை** ஆக இருக்க வேண்டும்.

    உங்கள் பதில்கள்:
    - **சரளமாகவும் சுருக்கமாகவும்** இருக்க வேண்டும் (புள்ளிவிவர வடிவத்தில்)
    - **காப்பீட்டு திட்டங்கள், பயன்கள் மற்றும் பாதுகாப்பை** மையமாகக் கொள்ள வேண்டும்
    - **நம்பகமான ஆதாரங்களை** அடிப்படையாகக் கொள்ள வேண்டும் (Ceylinco Life)

    நீங்கள் இந்த மூலத்தை பார்க்கலாம்:
    {urls}

    கேள்விக்கான பதிலை வழங்குவதற்கு முன்பு, உங்களை வரவேற்று ஒரு நட்பான அறிமுகத்துடன் தொடங்குங்கள்.

    கேள்வி: {question}

    பதில்:
    """

    # Sinhala Prompt Template
    template_si = f"""ඔබ විශ්වාසදායක රක්ෂණ සහයකයෙකි. ඔබ සපයන තොරතුරු **නිරවද්‍ය**, **විශ්වාසදායක**, සහ **යාවත්කාලීන** විය යුතුය.

    ඔබේ පිළිතුරු:
    - **සරල හා ක්රමානුකූල** විය යුතුය (ලකුණු වශයෙන්)
    - **රක්ෂණ ප්රතිපත්ති, ප්රතිලාභ සහ ආවරණය** කෙරෙහි අවධානය යොමු කරන්න
    - **විශ්වසනීය මූලාශ්ර** මත පදනම් විය යුතුය (Ceylinco Life)

    ඔබට මෙම මූලාශ්රය භාවිතා කළ හැක:
    {urls}

    ප්රශ්නයට පිළිතුරු දීමට පෙර, සාධරණ හා ආකර්ශනීය ආරම්භයක් සහිතව පිළිතුර ආරම්භ කරන්න.

    ප්රශ්නය: {question}

    පිළිතුර:
    """

    # Select appropriate language template
    if lang == 'ta':
        prompt_text = template_ta
    elif lang == 'si':
        prompt_text = template_si
    else:
        prompt_text = template_en  # Default to English

    print(f"🔍 Detected Language: {lang}")  # Debugging: Show detected language

    # Groq API call
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt_text}],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,  # Avoid issues with streaming
            stop=None,
        )

        # Directly return the response
        return completion.choices[0].message.content.strip()

    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("\nEnter your insurance question (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        response = get_response(user_input)
        print("\nResponse:\n", response)
