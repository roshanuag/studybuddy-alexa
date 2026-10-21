from flask import Flask, request, jsonify, send_from_directory
import agent
import memory

app = Flask(__name__)
chat = None    # one chat session at a time (fine for a demo)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.post("/start")
def start():
    global chat
    chat = agent.make_chat()
    return jsonify(reply=agent.start_session(chat))


@app.post("/chat")
def chat_route():
    if chat is None:
        return jsonify(reply="Please start a session first."), 400
    message = request.json.get("message", "")
    return jsonify(reply=agent.send(chat, message))


@app.get("/tasks")
def tasks():
    return jsonify(memory.load_tasks())


if __name__ == "__main__":
    app.run(debug=True)