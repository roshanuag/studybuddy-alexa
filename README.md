# StudyBuddy

A voice study coach in the style of Alexa+. It remembers your study tasks across sessions, checks in on what you missed, builds revision plans for exams, and quizzes you out loud.

**Track:** Alexa+ (simulated Alexa+ experience, built as a web app with an AI agent)

## What it does

- **Missed-task check-in:** every session starts by checking which tasks you missed and offering to reschedule them.
- **Talk to your plan:** add, finish, or move tasks by voice ("Move the DBMS assignment to Friday").
- **Revision plans:** "My Computer Networks exam is on Wednesday, topics are OSI model, TCP vs UDP and routing" creates a dated plan that avoids days you're already busy, plus a full-revision session and the exam itself.
- **Quiz mode:** "Quiz me on the OSI model" asks one question at a time, corrects your answers, gives a score, and offers to mark the topic done if you get everything right.
- **Live plan panel:** the plan updates and highlights whatever the agent just changed.

## How it works

```
Browser (index.html)
  speech recognition + speech synthesis (Web Speech API), animated orb (Canvas)
        |
        v
Flask server (app.py)  ->  /start, /chat, /tasks
        |
        v
Agent (agent.py)  ->  Gemini with automatic function calling
        |
        v
Tools (memory.py)  ->  add_task, add_plan, mark_done, reschedule_task, get_missed, load_tasks
        |
        v
tasks.json (persistent memory between sessions)
```

## Design decisions

- **Critical behaviour lives in code, not only in the prompt.** The missed-task check runs in code at the start of every session, and `add_plan` itself adds the exam and the full-revision day and rejects topics scheduled on or after the exam. Testing showed the model didn't follow these rules reliably from the prompt alone.
- **One tool call for a whole plan.** `add_plan` saves every topic in a single call, which means fewer round trips to the model and faster replies.
- **Failure handling:** a 30-second timeout, plus retries with exponential backoff on 429/500/503/504 errors, so the app shows a clear message instead of freezing. Tested by forcing a 1 ms timeout.
- **Review before send:** speech is transcribed into the text box so you can fix recognition mistakes before they reach your plan.
- **Correct dates:** the prompt includes the weekday, so "Friday" resolves to the right date.

## Setup

**You need:** Python 3.10 or newer, a free Gemini API key from [Google AI Studio](https://aistudio.google.com), and Chrome or Edge (for voice input).

```bash
git clone https://github.com/roshanuag/studybuddy-alexa.git
cd studybuddy-alexa
pip install -r requirements.txt
```

Create a file named `.env` in the project folder:

```
GEMINI_API_KEY=your_key_here
```

Run the web app:

```bash
python app.py
```

Open http://127.0.0.1:5000, click **Start session**, and allow microphone access.

To try it in the terminal instead, run `python agent.py`.

## Known limitations

- One user and one chat session at a time.
- Uses the Gemini free tier (`gemini-3.5-flash-lite`), so replies can be slow and there's a daily request limit. The model is set in one place (`MODEL` in `agent.py`).
- If a request times out after the model has already called a tool, the retry could repeat that action.
- Runs Flask's development server in debug mode, which is for local use only.

## Future work

- Run as a real Alexa+ integration through an MCP server.
- Spaced-repetition reminders based on quiz scores.
- Support for multiple users.

## License

MIT