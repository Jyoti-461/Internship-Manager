// Teacher's live chat reply page (templates/teacher/chat_reply.html).
// Joins the conversation's SocketIO room, sends/receives messages instantly,
// and lets the teacher mark the conversation resolved.

const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const resolveBtn = document.getElementById("resolveBtn");

function appendBubble(text, senderType) {
    const bubble = document.createElement("div");
    const sideClass = senderType === "teacher" ? "mine" : "theirs";
    bubble.className = `chat-bubble chat-bubble-${sideClass}`;
    bubble.innerHTML = `<span class="chat-sender">${senderType}</span><p></p>`;
    bubble.querySelector("p").textContent = text;
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {
    socket.emit("join_conversation", { conversation_id: CONVERSATION_ID });
    chatWindow.scrollTop = chatWindow.scrollHeight;
});

socket.on("new_message", (msg) => {
    if (msg.conversation_id !== CONVERSATION_ID) return;
    if (msg.sender_type === "teacher" && msg.sender_id === CURRENT_USER.id) return; // already shown locally
    appendBubble(msg.message_text, msg.sender_type);
});

chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;

    appendBubble(text, "teacher");
    socket.emit("send_chat_message", { conversation_id: CONVERSATION_ID, message: text });
    chatInput.value = "";
});

resolveBtn.addEventListener("click", () => {
    if (confirm("Mark this conversation as resolved?")) {
        socket.emit("mark_resolved", { conversation_id: CONVERSATION_ID });
        resolveBtn.disabled = true;
        resolveBtn.textContent = "Resolved";
    }
});
