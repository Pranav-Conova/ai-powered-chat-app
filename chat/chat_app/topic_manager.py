import threading
import time
import google.generativeai as genai
import asyncio
import random
from django.conf import settings
from channels.layers import get_channel_layer

current_topic = "Welcome to the chatroom!"
recent_topics = set()

configured = False

def generate_topic():
    global recent_topics, configured

    if not configured:
        genai.configure(api_key=settings.API_KEY)
        configured = True

    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")
    randomness = random.randint(1000, 9999)
    prompt = (
        f"Suggest a unique futuristic group discussion topic. "
        f"It must start with 'Topic:', be under 12 words, and avoid any symbols or numbers."
    )

    for _ in range(5):
        response = model.generate_content(prompt)
        topic = response.text.strip()

        if topic not in recent_topics:
            recent_topics.add(topic)
            if len(recent_topics) > 20:
                recent_topics.pop()
            return topic

    return "Let's discuss something new today!"

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
        time.sleep(60)

def start_topic_thread():
    thread = threading.Thread(target=topic_updater, daemon=True)
    thread.start()

chat_history = []

def add_message(message, user_id):
    chat_history.append({
        "message": message,
        "user_id": user_id
    })

def get_chat_history():
    return chat_history
