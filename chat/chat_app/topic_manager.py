import threading
import time
import google.generativeai as genai
import asyncio
import random
from channels.layers import get_channel_layer

genai.configure(api_key="AIzaSyDnmUhJwoif1cC6WL_ZV8dsFdpQ1oaLBkI")

current_topic = "Welcome to the chatroom!"  # default fallback topic
recent_topics = set()  # store recent topics to avoid repetition

def generate_topic():
    global recent_topics

    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")

    # Add randomness in the prompt
    randomness = random.randint(1000, 9999)
    prompt = f"Suggest a unique futuristic group discussion topic. It must start with 'Topic:', be under 12 words, and avoid any symbols or numbers."


    for _ in range(5):  # try up to 5 times to get a unique topic
        response = model.generate_content(prompt)
        topic = response.text.strip()

        # Avoid duplicates
        if topic not in recent_topics:
            recent_topics.add(topic)

            # Keep recent_topics set small (e.g., max 20)
            if len(recent_topics) > 20:
                recent_topics.pop()

            return topic

    return "Let's discuss something new today!"  # fallback if all attempts fail

async def broadcast_topic(new_topic):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        "chat_topic",
        {
            "type": "send_new_topic",
            "message": f"New Topic: {new_topic}"
        }
    )

def topic_updater():
    global current_topic
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:
        try:
            new_topic = generate_topic()
            current_topic = new_topic
            print("Generated topic:", new_topic)
            loop.run_until_complete(broadcast_topic(new_topic))
        except Exception as e:
            print("Error updating topic:", e)
        time.sleep(60)  # wait for 1 minute

def start_topic_thread():
    thread = threading.Thread(target=topic_updater, daemon=True)
    thread.start()

# chat_store.py
chat_history = []

def add_message(message, user_id):
    chat_history.append({
        "message": message,
        "user_id": user_id
    })

def get_chat_history():
    return chat_history
