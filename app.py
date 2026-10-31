
import os
from flask import Flask, request, jsonify, render_template_string
from google import genai

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JARVIS AI</title>
<style>
body {
  background:#07111f;
  color:white;
  font-family:Arial;
  text-align:center;
  padding:20px;
}
h1 {color:#35c8ff; margin-top:35px;}
#chat {
  max-width:600px;
  margin:20px auto;
  text-align:left;
}
.msg {
  background:#14243a;
  padding:13px;
  border-radius:12px;
  margin:12px 0;
  white-space:pre-wrap;
}
input {
  width:68%;
  padding:14px;
  border-radius:10px;
  border:0;
}
button {
  padding:14px;
  background:#168ed0;
  color:white;
  border:0;
  border-radius:10px;
}
</style>
</head>
<body>
<h1>J.A.R.V.I.S</h1>
<p>Your Personal AI Assistant</p>
<div id="chat"></div>
<input id="message" placeholder="Bolo bhai, kya karna hai?">
<button onclick="send()">Send</button>
<script>
async function send() {
  const input = document.getElementById("message");
  const msg = input.value.trim();
  if (!msg) return;
  input.value = "";

  const chat = document.getElementById("chat");
  const user = document.createElement("div");
  user.className = "msg";
  user.textContent = "You: " + msg;
  chat.appendChild(user);

  const reply = document.createElement("div");
  reply.className = "msg";
  reply.textContent = "JARVIS: Thinking...";
  chat.appendChild(reply);

  try {
    const res = await fetch("/chat", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:msg})
    });
    const data = await res.json();
    reply.textContent = "JARVIS: " + (data.reply || data.error);
  } catch(e) {
    reply.textContent = "JARVIS: Connection error.";
  }
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/health")
def health():
    return jsonify({"status":"JARVIS online"})

@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message", "").strip()

    if not message:
        return jsonify({"error":"Please enter a message"}), 400

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error":"AI key is not configured yet"}), 503

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=message,
            config={
                "system_instruction":
                "You are JARVIS, a smart personal AI assistant. "
                "Speak naturally in Hindi or English according to the user. "
                "Be helpful, friendly and concise. "
                "Never claim to control an app or device unless an actual "
                "authorized integration has performed that action."
            }
        )
        return jsonify({"reply": response.text or "No response received."})

    except Exception:
        app.logger.exception("Gemini request failed")
        return jsonify({"error":"AI service error. Please try again."}), 502

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
  
