async function sendMessage() {
  const input = document.getElementById("message-input");
  const chatBox = document.getElementById("chat-box");

  const message = input.value.trim();
  if (!message) return;

  chatBox.innerHTML += `<div class="user message">${escapeHtml(message)}</div>`;
  input.value = "";

  const response = await fetch("/agent/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ message })
  });

  const data = await response.json();
  const botMessage = data.response || data.message || JSON.stringify(data, null, 2);

  chatBox.innerHTML += `<div class="bot message">${escapeHtml(botMessage)}</div>`;
  chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;")
    .replaceAll("\n", "<br>");
}


document.getElementById("message-input").addEventListener("keydown", function(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});
