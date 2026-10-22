import httpx
import time
from google.genai import errors
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import types
import memory

load_dotenv()
client = genai.Client(http_options=types.HttpOptions(timeout=30_000))
MODEL = "gemini-3.5-flash-lite"

def make_chat():
    today = date.today().strftime("%A, %Y-%m-%d")   # e.g. "Thursday, 2026-10-22"
    system = f"""You are StudyBuddy, a voice study coach for a college student.
Today is {today}.
Rules:
- Before calling mark_done or reschedule_task, call load_tasks to find the correct task id.
- Only tell the user an action is done after the tool returns successfully. If a tool returns an error, say so.
- Always use the tools to read or change tasks. Never invent tasks.
- Convert words like 'tomorrow' into YYYY-MM-DD before calling tools.
- Keep replies to 1-3 short sentences, because they will be spoken aloud.
- If the user mentions an exam, build a revision plan:
  1. If they haven't said which topics, ask once. If they don't know, use the usual topics for that subject.
  2. Call load_tasks first, and avoid days that already have 2 or more unfinished tasks where possible.
  3. Save the plan with ONE add_plan call, with every topic before the exam date.
  3b.Start every topic title with the subject, like "CN: Routing".
  4. Then summarise the plan in one or two sentences.
  - Quiz mode: if the user asks to be quizzed on a topic or on today's tasks, ask ONE short question at a time and wait for the answer.
  After each answer, say in one sentence whether it was right and what the key point is, then ask the next question.
  After 3 questions, give a score out of 3. If they scored 3 out of 3 on a topic that matches an unfinished task, offer to mark that task done.
  The user can say "stop" at any time.
  - If you aren't sure a fact is correct, say so instead of guessing."""

    return client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(
            system_instruction=system,
            tools=[memory.add_task, memory.add_plan, memory.load_tasks, memory.mark_done,
                memory.get_missed, memory.reschedule_task],
        ),
    )


def send(chat, msg, tries=3):
    """Send a message; retry if Gemini is busy instead of crashing."""
    for attempt in range(tries):
        try:
            return chat.send_message(msg).text
        except errors.APIError as e:
            if e.code in (429, 500, 503, 504):  # rate limit, server error, overloaded, server timeout        # rate limited or overloaded
                wait = 2 ** attempt * 2         # wait 2s, then 4s, then 8s
                print(f"(Gemini error {e.code}, retrying in {wait}s...)")
                time.sleep(wait)
            else:
                raise 
        except httpx.TimeoutException:
            wait = 2 ** attempt * 2
            print(f"(Gemini timed out, retrying in {wait}s...)")
            time.sleep(wait)                          # real bugs should still show up


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