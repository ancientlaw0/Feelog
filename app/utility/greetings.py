import random
from datetime import datetime

# Random greeting according to the time of the day

def get_dynamic_greeting(username: str) -> str:
    GREETING_POOL = {
        "morning": [
            "Good morning, {username}. Let’s start fresh.",
            "Good morning, {username}. The early calm hits different.",
            "Rise and shine, {username}. The mint is strong today. 🌱",
            "Hello, {username}. A fresh day, a fresh start. ✨",
            "Morning, {username}. Time to realign and refocus. 💡",
            "Good morning, {username}. Take a deep breath — the day’s yours. 🫧",
            "Welcome back, {username}. Let’s build something meaningful. 🧱",
            "Top of the morning, {username}. You’ve got this. ☀️"
        ],
        "afternoon": [
            "Good afternoon, {username}. Let’s keep the momentum going. 🔄",
            "Hello again, {username}. You’re halfway through — stay steady. 🌿",
            "Good afternoon, {username}. Small steps. Big changes. 💡",
            "Hi, {username}. Your calm focus is your superpower. 🧠",
            "Welcome back, {username}. Keep moving, but don’t rush. 🫧",
            "Hey there, {username}. Ready for a focused flow session? 💻",
            "Good afternoon, {username}. One mindful action at a time. ✨",
            "Good to see you, {username}. Let’s shape the rest of your day. 🧩"
        ],
        "evening": [
            "Good evening, {username}. Reflect and refresh. 🌙",
            "Welcome back, {username}. You’ve earned your calm. 🫧",
            "Evening, {username}. Let the quiet guide you. 🌌",
            "Hey, {username}. Breathe in, slow down, stay soft. 🌿",
            "Good evening, {username}. Let the noise fade. You’re doing well. 🔕",
            "Hello, {username}. The day’s done. You showed up — that’s enough. 💫",
            "Evening vibes, {username}. Gentle focus or gentle rest — your call. 🎧",
            "Nice to see you, {username}. Let’s wind down with meaning. 🔎"
        ]
    }

    hour = datetime.now().hour

    if hour < 12:
        period = "morning"
    elif hour < 18:
        period = "afternoon"
    else:
        period = "evening"

    return random.choice(GREETING_POOL[period]).format(username=username)
