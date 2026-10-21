import time
from google.genai import errors
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import types
import memory

load_dotenv()
client = genai.Client()

def make_chat():
    today = date.today().isoformat()
    system = f"""You are StudyBuddy, a voice study coach for a college student.
Today is {today}.
Rules:
- Before calling mark_done or reschedule_task, call load_tasks to find the correct task id.
- Only tell the user an action is done after the tool returns successfully. If a tool returns an error, say so.
- Always use the tools to read or change tasks. Never invent tasks.
- Convert words like 'tomorrow' into YYYY-MM-DD before calling tools.
- Keep replies to 1-3 short sentences, because they will be spoken aloud."""

    return client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=system,
            tools=[memory.add_task, memory.load_tasks, memory.mark_done,
                   memory.get_missed, memory.reschedule_task],
        ),
    )


def send(chat, msg, tries=3):
    """Send a message; retry if Gemini is busy instead of crashing."""
    for attempt in range(tries):
        try:
            return chat.send_message(msg).text
        except errors.APIError as e:
            if e.code in (429, 503):            # rate limited or overloaded
                wait = 2 ** attempt * 2         # wait 2s, then 4s, then 8s
                print(f"(Gemini is busy, retrying in {wait}s...)")
                time.sleep(wait)
            else:
                raise                           # real bugs should still show up
    return "Sorry, I can't reach my brain right now. Please try again in a minute."

def start_session(chat):
    """Check missed tasks in code, then have the AI greet the user."""
    missed = memory.get_missed(date.today().isoformat())
    return send(chat, f"[Session started. Missed tasks: {missed}] "
                      "Greet the user. If there are missed tasks, name them and offer to reschedule.")


if __name__ == "__main__":
    chat = make_chat()
    opening = start_session(chat)
    print("StudyBuddy:", opening)

    while True:
        msg = input("You: ")
        if msg.lower() == "quit":
            break
        reply = send(chat, msg)
        print("StudyBuddy:", reply)