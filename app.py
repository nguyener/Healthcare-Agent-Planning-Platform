from flask import Flask, request, jsonify

from app.agent.agent_service import AgentService
from app.tools.tool_registry import build_tool_registry

app = Flask(__name__)

agent_service = AgentService(build_tool_registry())


@app.route("/", methods=["GET"])
def home():
    return "Patient Engagement AI Agent is running."


@app.route("/agent/chat", methods=["GET"])
def agent_chat_info():
    return {
        "message": "Use POST /agent/chat with JSON body: {\"message\": \"...\"}"
    }

@app.route("/agent/chat", methods=["POST"])
def agent_chat():
    data = request.get_json() or {}

    message = data.get("message")
    if not message:
        return jsonify({"error": "message is required"}), 400

    result = agent_service.run(message)

    return jsonify(result), 200

if __name__ == "__main__":
    app.run(debug=True, port=5050)