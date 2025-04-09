import google.generativeai as genai
from django.conf import settings

genai.configure(api_key="AIzaSyDnmUhJwoif1cC6WL_ZV8dsFdpQ1oaLBkI")

def get_ai_topic():
    prompt = "Generate a fun, creative topic that people can talk about in a group chat. Make it open-ended and imaginative."

    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)

    return response.text.strip()
