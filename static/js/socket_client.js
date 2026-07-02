// Shared SocketIO client connection, used by both the student chat page
// and the teacher chat_reply page. Assumes the socket.io script tag and
// CURRENT_USER global are already defined in the page before this loads.

const socket = io();

socket.on("connect", () => {
    console.log("Connected to chat server as", CURRENT_USER.role, CURRENT_USER.id);
});

socket.on("error", (data) => {
    console.error("Socket error:", data.msg);
});

socket.on("disconnect", () => {
    console.log("Disconnected from chat server.");
});
