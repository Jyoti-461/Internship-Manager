// Student chat widget.
// Two modes, decided by the server's "handled_by" field on each conversation:
//   - "bot": messages POST to /api/chat/send (REST), bot replies instantly
//   - "teacher": messages go over the SocketIO room "conversation_<id>" for
//                true real-time chat with the assigned teacher
//
// On page load we fetch chat history to figure out which mode we're in,
// and switch live if a bot escalation flips it to "teacher" mid-conversation.

const chatWindow = document.getElementById("chatWindow");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const chatStatusBanner = document.getElementById("chatStatusBanner");

let currentMode = "bot";       // "bot" | "teacher"
let conversationId = null;
let socketJoined = false;

function appendBubble(text, senderType) {
    const bubble = document.createElement("div");
    const sideClass = senderType === "student" ? "mine" : (senderType === "bot" ? "bot" : "theirs");
    bubble.className = `chat-bubble chat-bubble-${sideClass}`;
    bubble.innerHTML = `<span class="chat-sender">${senderType}</span><p></p>`;
    bubble.querySelector("p").textContent = text; // textContent avoids XSS
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTyping() {
    const el = document.createElement("div");
    el.className = "typing-indicator";
    el.id = "typingIndicator";
    el.textContent = "InternBot is typing...";
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById("typingIndicator");
    if (el) el.remove();
}

function updateBanner() {
    if (currentMode === "teacher") {
        chatStatusBanner.textContent = "You're now connected with a coordinator. They'll reply here directly.";
        chatStatusBanner.style.background = "#dcfce7";
        chatStatusBanner.style.color = "#166534";
    } else {
        chatStatusBanner.textContent = "Chatting with InternBot — ask about eligibility, documents, stipend, and more.";
        chatStatusBanner.style.background = "#eff6ff";
        chatStatusBanner.style.color = "#1e40af";
    }
}

async function loadHistory() {
    const res = await fetch("/api/chat/history");
    const data = await res.json();

    chatWindow.innerHTML = "";
    conversationId = data.conversation_id || null;
    currentMode = data.handled_by || "bot";
    updateBanner();

    if (data.messages && data.messages.length) {
        data.messages.forEach(m => appendBubble(m.message_text, m.sender_type));
    } else {
        appendBubble("Hi! I'm InternBot 👋 Ask me anything about our internship program — eligibility, duration, stipend, documents needed, or how to apply.", "bot");
    }

    if (currentMode === "teacher" && conversationId && !socketJoined) {
        joinLiveChat(conversationId);
    }
}

function joinLiveChat(convId) {
    socketJoined = true;
    socket.emit("join_conversation", { conversation_id: convId });

    socket.on("new_message", (msg) => {
        if (msg.conversation_id !== conversationId) return;
        // Don't double-render the student's own message (already shown on send)
        if (msg.sender_type === "student" && msg.sender_id === CURRENT_USER.id) return;
        appendBubble(msg.message_text, msg.sender_type);
    });

    socket.on("conversation_resolved", () => {
        appendBubble("This conversation has been marked as resolved by your coordinator.", "teacher");
    });
}

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;

    appendBubble(text, "student");
    chatInput.value = "";

    if (currentMode === "teacher" && conversationId) {
        // Live mode: send over socket, teacher sees it instantly
        socket.emit("send_chat_message", { conversation_id: conversationId, message: text });
        return;
    }

    // Bot mode: REST call
    showTyping();
    try {
        const res = await fetch("/api/chat/send", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text }),
        });
        const data = await res.json();
        hideTyping();

        if (data.error) {
            appendBubble("Sorry, something went wrong. Please try again.", "bot");
            return;
        }

        conversationId = data.conversation_id;

        if (data.handled_by === "teacher" && currentMode !== "teacher") {
            // Already escalated and claimed before this message
            currentMode = "teacher";
            updateBanner();
            if (!socketJoined) joinLiveChat(conversationId);
            appendBubble(data.message || "Your message has been sent to your coordinator.", "teacher");
            return;
        }

        appendBubble(data.reply, "bot");

        if (data.escalated) {
            currentMode = "escalated"; // still bot-handled until a teacher claims it
            chatStatusBanner.textContent = "Your query has been forwarded to our team — they'll join this chat shortly.";
            chatStatusBanner.style.background = "#fef3c7";
            chatStatusBanner.style.color = "#92400e";
        }
    } catch (err) {
        hideTyping();
        appendBubble("Sorry, I'm having trouble connecting right now. Please try again in a moment.", "bot");
    }
});

document.addEventListener("DOMContentLoaded", loadHistory);
